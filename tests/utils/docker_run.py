import docker


class DockerRun:
    def __init__(self, image, command=None, **kwargs):
        self.client = docker.from_env()
        self.client.images.pull(image, tag=self._image_tag(image))
        self.container = self.client.containers.run(
            image, command, **kwargs,
            detach=True,
            remove=True,
        )

    @staticmethod
    def _image_tag(image) -> str:
        try:
            return image.split(':')[1]
        except IndexError:
            return 'latest'

    def __enter__(self):
        return self.container

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.container.kill()
            self.client.close()
        except docker.errors.APIError:
            pass
