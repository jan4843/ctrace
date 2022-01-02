#include <linux/cgroup.h>
#include <linux/pid_namespace.h>
#include <linux/sched.h>

#define CONTAINER_ID_LEN 64
#define CONTAINER_ID_SHORT_LEN 12
#define STRING_MAX_LEN 32

struct container
{
    char id[CONTAINER_ID_LEN + 1];
};

struct container_key
{
    struct container container;
    int key;
};

struct string
{
    char value[STRING_MAX_LEN + 1];
};

#ifdef DEBUG
BPF_HASH(capability_names, int, struct string);
BPF_HASH(syscall_names, int, struct string);
#endif

BPF_HASH(pid_to_container, int, struct container);
BPF_HASH(runc_has_run, struct container, int);
BPF_HASH(runc_not_finished, struct container, int);

BPF_HASH(container_capability_count, struct container_key, int);
BPF_HASH(container_syscall_count, struct container_key, int);

#define READ_KERNEL(ptr) (                         \
    {                                              \
        typeof(ptr) _val;                          \
        bpf_probe_read(&_val, sizeof(_val), &ptr); \
        _val;                                      \
    })

static struct container_key container_key_init(struct container container, int key)
{
    struct container_key container_key;
    __builtin_memset(&container_key, 0, sizeof(container_key));
    container_key.container = container;
    container_key.key = key;
    return container_key;
}

static bool is_cap_allowed(struct task_struct *task, int cap)
{
    struct cred *real_cred = (struct cred *)READ_KERNEL(task->real_cred);
    kernel_cap_t caps = real_cred->cap_effective;
    u64 contiguous_caps = ((caps.cap[1] + 0ULL) << 32) + caps.cap[0];
    u64 cap_bit = 1 << cap;
    return contiguous_caps & cap_bit;
}

static struct task_struct *get_current_task()
{
    return (struct task_struct *)bpf_get_current_task();
}

static int get_global_pid(struct task_struct *task)
{
    return task->pid;
}

static int get_namespaced_pid(struct task_struct *task)
{
    struct nsproxy *nsproxy = task->nsproxy;
    struct pid_namespace *pid_ns_children = nsproxy->pid_ns_for_children;
    unsigned int level = pid_ns_children->level;
    struct pid *tpid = task->thread_pid;
    return tpid->numbers[level].nr;
}

static inline void get_container_id(struct cgroup *cgroup, struct container *container)
{
    const char *dirname = cgroup->kn->name;
    for (int i = 0; i < CONTAINER_ID_LEN; i++)
        container->id[i] = *(dirname + i);
    container->id[CONTAINER_ID_LEN] = 0;
}

static inline int get_container(struct task_struct *task, struct container *container)
{
    int pid = get_global_pid(task);

    struct container *container_ptr = (struct container *)pid_to_container.lookup(&pid);
    if (container_ptr == NULL)
        return false;

    for (int i = 0; i < sizeof(container->id); i++)
        container->id[i] = container_ptr->id[i];

    return true;
}

#ifdef DEBUG
static inline void get_capability_name(int id, char *name)
{
    struct string *string_ptr = (struct string *)capability_names.lookup(&id);
    if (string_ptr == NULL)
        return;

    for (int i = 0; i < STRING_MAX_LEN; i++)
        name[i] = string_ptr->value[i];
}

static inline void get_syscall_name(int id, char *name)
{
    struct string *string_ptr = (struct string *)syscall_names.lookup(&id);
    if (string_ptr == NULL)
        return;

    for (int i = 0; i < STRING_MAX_LEN; i++)
        name[i] = string_ptr->value[i];
}
#endif

static inline bool is_runc()
{
    char comm[TASK_COMM_LEN];
    bpf_get_current_comm(&comm, sizeof(comm));
    char runc[] = "runc:";

    bool is_runc = true;
    for (int i = 0; i < sizeof(runc) - 1; i++)
        if (comm[i] != runc[i])
            is_runc = false;

    return is_runc;
}

static inline bool get_runc_finished(struct container container)
{
    if (is_runc())
    {
        int zero = 0;
        runc_has_run.insert(&container, &zero);
    }
    else if (runc_has_run.lookup(&container) != NULL)
    {
        runc_not_finished.delete(&container);
    }

    if (runc_not_finished.lookup(&container) == NULL)
    {
        runc_has_run.delete(&container);
        return true;
    }
    return false;
}

static inline void set_runc_not_finished(struct container container)
{
    int zero = 0;
    runc_not_finished.insert(&container, &zero);
}

#ifdef DEBUG
static void print_event(struct container *container, char *type, char *value)
{
    char message[128] = {0};
    int i = 0;

    message[i++] = '[';
    for (int j = 0; j < CONTAINER_ID_SHORT_LEN; j++)
        message[i++] = container->id[j];
    message[i++] = ']';

    message[i++] = ' ';
    for (int j = 0; j < STRING_MAX_LEN; j++)
        if (type[j] == '\0')
            break;
        else
            message[i++] = type[j];

    message[i++] = ' ';
    for (int j = 0; j < STRING_MAX_LEN; j++)
        if (value[j] == '\0')
            break;
        else
            message[i++] = value[j];

#if LINUX_VERSION_CODE < KERNEL_VERSION(5, 10, 0)
    bpf_trace_printk("%s\n", message);
#else
    bpf_trace_printk("%s", message);
#endif
}
#endif

int raw_tracepoint__cgroup_attach_task(struct bpf_raw_tracepoint_args *ctx)
{
    struct cgroup *dst_cgrp = (struct cgroup *)ctx->args[0];
    const char *path = (char *)ctx->args[1];
    struct task_struct *task = (struct task_struct *)ctx->args[2];
    bool threadgroup = ctx->args[3];
    {
        struct container container;
        get_container_id(dst_cgrp, &container);
        int pid = get_global_pid(task);

        set_runc_not_finished(container);
        pid_to_container.insert(&pid, &container);

        return 0;
    }
}

int raw_tracepoint__sched_process_fork(struct bpf_raw_tracepoint_args *ctx)
{
    struct task_struct *parent = (struct task_struct *)ctx->args[0];
    struct task_struct *child = (struct task_struct *)ctx->args[1];
    {
        struct container container;
        if (!get_container(parent, &container))
            return 0;

        int child_pid = get_global_pid(child);
        pid_to_container.insert(&child_pid, &container);

        return 0;
    }
}

int raw_tracepoint__sched_process_exit(struct bpf_raw_tracepoint_args *ctx)
{
    struct task_struct *p = (struct task_struct *)ctx->args[0];
    {
        int pid = get_global_pid(p);
        pid_to_container.delete(&pid);

        return 0;
    }
}

#ifdef TRACE_RUNC
BPF_HASH(runc_pid, struct container, int);
#endif

int raw_tracepoint__sys_enter(struct bpf_raw_tracepoint_args *ctx)
{
    struct pt_regs *regs = (struct pt_regs *)ctx->args[0];
    long id = ctx->args[1];
    {
        struct task_struct *current_task = get_current_task();

        struct container container;
        if (!get_container(current_task, &container))
            return 0;

        if (!get_runc_finished(container))
        {
#ifdef TRACE_RUNC
            if (is_runc())
            {
                int pid = get_global_pid(current_task);

                if (id == __NR_seccomp)
                    runc_pid.lookup_or_try_init(&container, &pid);

                int *runc_pid_ptr = runc_pid.lookup(&container);
                if (runc_pid_ptr == NULL || pid != *runc_pid_ptr)
                {
                    return 0;
                }
            }
            else
            {
                return 0;
            }
#else
            return 0;
#endif
        }

#ifdef DEBUG
        char syscall_name[STRING_MAX_LEN] = "?";
        get_syscall_name(id, syscall_name);
        print_event(&container, "sys", syscall_name);
#endif

        struct container_key container_key = container_key_init(container, id);
        container_syscall_count.increment(container_key);

        return 0;
    }
}

int kprobe__cap_capable(struct pt_regs *ctx,
                        const struct cred *cred, struct user_namespace *targ_ns, int cap, int cap_opt)
{
    struct task_struct *current_task = get_current_task();

    struct container container;
    if (!get_container(current_task, &container))
        return 0;

    if (!get_runc_finished(container))
        return 0;

    if (!is_cap_allowed(current_task, cap))
        return 0;

#ifdef DEBUG
    char capability_name[STRING_MAX_LEN] = "?";
    get_capability_name(cap, capability_name);
    print_event(&container, "cap", capability_name);
#endif

    struct container_key container_key = container_key_init(container, cap);
    container_capability_count.increment(container_key);

    return 0;
}
