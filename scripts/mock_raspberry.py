import io


class MockFileWithDecode:
    def __init__(self, input_string: str):
        byte_string = input_string.encode('utf-8')
        self.data = byte_string

    def read(self):
        # Return an object that has a decode method
        return MockReadResult(self.data)


class MockReadResult:
    def __init__(self, data):
        self.data = data

    def decode(self, encoding='utf-8'):
        # Mimic the behavior of decode
        return self.data.decode(encoding)


class MockRaspberry:
    def __init__(self):
        pass

    def close(self):
        pass

    def connect(self, *args, **kwargs):
        pass

    def exec_command(self, command: str):
        print(command)
        if command.startswith("cat /home/pi/Pigrow/config/pigrow_config.txt"):
            target = command.split(' ')[-1]
            output = self.cat_config(target)
        else:
            output = "Hello"

        stdin = MockFileWithDecode(command)
        stdout = MockFileWithDecode(output)
        stderr = MockFileWithDecode("")
        return stdin, stdout, stderr

    def cat_config(self, target):
        return 'box_name="Pigrow2 - veg"'
