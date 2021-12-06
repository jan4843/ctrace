def get_pid_command(pid: int):
    with open(f'/proc/{pid}/cmdline', 'r', encoding='ascii') as cmd:
        return cmd.read().split('\x00')[:-1]
