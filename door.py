'''from cp_abe import cp_abe

def get_pw():
    count = input('Number of attributes:')
    attrs = []
    for i in range(int(count)):
        attrs.append(input('Enter your attributes: ').upper())
    return attrs

def main():
    #User enter attributes
    attrs = get_pw()
    ##verify attributes and generate OTP
    otp = cp_abe(attrs)
    return otp

if __name__ == '__main__':
    a = main()
    print(a)
    '''
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from cp_abe import cp_abe

class AttributeVerifierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attribute Verifier")

        # Load and display a pattern image
        self.pattern_image = Image.open("pattern.png")
        self.pattern_photo = ImageTk.PhotoImage(self.pattern_image)
        self.pattern_label = ttk.Label(root, image=self.pattern_photo)
        self.pattern_label.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S), rowspan=4)

        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(column=1, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.label_count = ttk.Label(self.main_frame, text="Number of attributes:")
        self.label_count.grid(column=0, row=0, sticky=tk.W, pady=10)

        self.count_entry = ttk.Entry(self.main_frame)
        self.count_entry.grid(column=1, row=0, sticky=(tk.W, tk.E), pady=10)

        self.attributes_frame = ttk.Frame(self.main_frame)
        self.attributes_frame.grid(column=0, row=1, columnspan=2, pady=10)

        self.attributes_labels = []
        self.attributes_entries = []

        self.input_attributes_button = ttk.Button(self.main_frame, text="Input Attributes", command=self.create_attribute_widgets)
        self.input_attributes_button.grid(column=0, row=2, pady=10)

        self.verify_button = ttk.Button(self.main_frame, text="Verify Attributes", command=self.verify_attributes)
        self.verify_button.grid(column=1, row=2, pady=10)
        self.verify_button.grid_remove()  # Ẩn nút Verify ban đầu

        self.result_label_frame = ttk.LabelFrame(self.main_frame, text="Result")
        self.result_label_frame.grid(column=0, row=3, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.result_label = ttk.Label(self.result_label_frame, text="")
        self.result_label.grid(column=0, row=0, sticky=tk.W)

    def create_attribute_widgets(self):
        count = int(self.count_entry.get())

        # Clear existing widgets
        for label in self.attributes_labels:
            label.destroy()
        for entry in self.attributes_entries:
            entry.destroy()

        self.attributes_labels = []
        self.attributes_entries = []

        # Create new widgets
        for i in range(count):
            label = ttk.Label(self.attributes_frame, text=f"Attribute {i + 1}:")
            label.grid(column=0, row=i, sticky=tk.W, pady=5)
            entry = ttk.Entry(self.attributes_frame)
            entry.grid(column=1, row=i, sticky=(tk.W, tk.E), pady=5)
            self.attributes_labels.append(label)
            self.attributes_entries.append(entry)

        # Ẩn nút "Input Attributes"
        self.input_attributes_button.grid_remove()
        # Hiển thị nút "Verify Attributes"
        self.verify_button.grid()

    def get_pw(self):
        attrs = [entry.get().upper() for entry in self.attributes_entries]
        return attrs

    def verify_attributes(self):
        attrs = self.get_pw()
        otp = cp_abe(attrs)
        if otp is not None:
            result_text = f"Generated OTP: {otp}"
        else:
            result_text = "FAIL"
        
        self.result_label.config(text=result_text)

if __name__ == '__main__':
    root = tk.Tk()
    app = AttributeVerifierApp(root)
    root.mainloop()

#Test case documentation
#prune list of attributtes
'''
attr1 = ['a','c','e']
attr2 = ['b','c','e']
attr3 = ['a','d','g','h']
'''