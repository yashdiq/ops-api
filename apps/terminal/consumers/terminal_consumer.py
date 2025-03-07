import os
import pty
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from config import settings

BASE_DIRECTORY = os.path.join(settings.BASE_DIR, "sandbox")

class TerminalConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.master_fd = None
        self.slave_fd = None
        self.process = None
        self.keep_alive_task = None
        self.loop = asyncio.get_event_loop()

    async def connect(self):
        try:
            os.makedirs(BASE_DIRECTORY, exist_ok=True)

            self.master_fd, self.slave_fd = pty.openpty()

            command = [
                "/bin/bash",
                "--noprofile",
                "--norc",
                "-i"
            ]

            self.process = await asyncio.create_subprocess_exec(
                *command,
                cwd=BASE_DIRECTORY,
                stdin=self.slave_fd,
                stdout=self.slave_fd,
                stderr=self.slave_fd,
                start_new_session=True,
                env={
                    "TERM": "xterm-256color",
                    "HOME": BASE_DIRECTORY,
                    "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
                    "PS1": "\\u@\\h:\\w\\$ ",
                    "SHELL": "/bin/bash",
                }
            )

            await self.accept()

            self.keep_alive_task = asyncio.create_task(self.keep_alive())

            self.loop.add_reader(self.master_fd, self._on_data)
        except Exception as e:
            print("Error during connect:", e)
            await self.close()

    def _on_data(self):
        try:
            data = os.read(self.master_fd, 1024)
            if data:
                asyncio.create_task(self.send(text_data=data.decode()))
            else:
                self.loop.remove_reader(self.master_fd)
                asyncio.create_task(self.close())
        except Exception as e:
            print(f"Read error: {e}")
            self.loop.remove_reader(self.master_fd)
            asyncio.create_task(self.close())

    async def disconnect(self, close_code):
        if self.master_fd is not None:
            try:
                self.loop.remove_reader(self.master_fd)
            except Exception as e:
                print("Error removing reader:", e)

        if self.keep_alive_task:
            self.keep_alive_task.cancel()

        if self.process and self.process.returncode is None:
            self.process.terminate()
            try:
                await self.process.wait()
            except ProcessLookupError:
                pass

        for fd in [self.master_fd, self.slave_fd]:
            if fd is not None:
                try:
                    os.close(fd)
                except OSError:
                    pass

    async def receive(self, text_data):
        if self.master_fd is not None:
            try:
                os.write(self.master_fd, text_data.encode())
            except OSError:
                await self.close()

    async def keep_alive(self):
        while True:
            await asyncio.sleep(30)
            try:
                await self.send(text_data="\x05")
            except Exception:
                break
