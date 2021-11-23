class DacClass:
    def __init__(self, name, IP):
        self.name = name
        self.address = IP
        self.active = True
        print(f'DAC {self.name} created')

    def get_data(self):
        pass

    def set_inactive(self):
        print(f'Marking {self.name} as inactive')
        self.active = False
        pass

    def set_active(self):
        print(f'Marking {self.name} as active')
        self.active = True
        pass
