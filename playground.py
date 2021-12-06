import docker

class DockerRun:
    def __init__(self, image, command=None, **kwargs):
        client = docker.DockerClient()
        client.images.pull(image, tag=self._tag(image))
        self.container = client.containers.run(
            image, command, **kwargs,
            detach=True,
        )

    @staticmethod
    def _tag(image):
        try:
            return image.split(':')[1]
        except IndexError:
            return 'latest'

    def __enter__(self):
        return self.container

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.container.kill()
        except docker.errors.APIError:
            pass

with DockerRun('busybox', 'sleep infinity') as c:
    print(c.id)
