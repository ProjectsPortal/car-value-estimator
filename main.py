import onnxruntime as ort
import numpy as np
import os
from datetime import date
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty, ListProperty, DictProperty
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.config import Config
import sys

Config.set('kivy', 'window_icon', 'car_icon.icns')

class HoverBehavior(object):
    hover_color = ListProperty([1, 1, 1, 1])
    normal_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos = self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        if inside:
            self.background_color = self.hover_color
        else:
            self.background_color = self.normal_color

class HoverButton(HoverBehavior, Button):
    pass

class MyLayout(BoxLayout):
    make = StringProperty()
    model = StringProperty()
    year = NumericProperty()
    miles = NumericProperty()
    condition = StringProperty()
    #slider_value = StringProperty()

    # Mappings for make and condition
    make_map = {
        'Acura': 10,
        'Audi': 11,
        'BMW': 12,
        'Chevrolet': 13,
        'Chrysler': 14,
        'Dodge': 15,
        'Ford': 16,
        'GMC': 17,
        'Honda': 18,
        'Hyundai': 19,
        'Jeep': 20,
        'Kia': 21,
        'Lexus': 22,
        'Mazda': 23,
        'Mercedes-Benz': 24,
        'Nissan': 25,
        'Porsche': 26,
        'Subaru': 27,
        'Tesla': 28,
        'Toyota': 29,
        'Volkswagen': 30,
        'Volvo': 31,
    }

    model_map = DictProperty({
        'Acura':        {'NSX':104, 'MDX':103, 'RDX': 102, 'TLX': 101, 'ILX': 100,},
        'Audi':         {'R8': 117, 'Q8': 116, 'A8': 115, 'Q7': 114, 'A6': 113, 'Q5': 112, 'A4': 111, 'Q3':110,},
        'BMW':          {'8 Series': 129, '7 Series': 128, 'X7': 127, 'X6': 126, 'X5': 125, '5 Series': 124, 
                         '3 Series': 123, 'X3': 122, '2 Series': 121, '1 Series': 120,},
        'Cadillac':     {'Escalade': 135, 'CT6': 134, 'XT6': 133, 'XT5': 132, 'CT5': 131, 'XT4': 130,},
        'Chevrolet':    {'Corvette': 149, 'Silverado': 148, 'Tahoe': 147, 'Suburban': 146, 'Traverse': 145, 'Equinox': 144,
                         'Malibu': 143, 'Trax': 142, 'Spark': 141, 'Sonic': 140, },
        'Chrysler':     {'Pacifica': 153, '300': 152, 'Voyager': 151, 'PT Cruiser': 150,},
        'Dodge':        {'Challenger': 164, 'Ram': 163, 'Charger': 162, 'Durango': 161, 'Journey': 160,},
        'Ford':         {'Mustang': 179, 'F-150': 178, 'Expedition': 177, 'Explorer': 176, 'Edge': 175, 'Escape': 174,
                         'Ranger': 173, 'Fusion': 172, 'EcoSport': 171, 'Fiesta': 170,},
        'GMC':          {'Sierra': 184, 'Yukon': 183, 'Acadia': 182, 'Terrain': 181, 'Canyon1': 180,},
        'Honda':        {'Odyssey': 198, 'Pilot': 197, 'Passport': 196, 'Ridgeline': 195, 'Accord': 194, 'CR-V': 193,
                         'Civic': 192, 'HR-V': 191, 'Fit': 190,},
        'Hyundai':      {'Palisade': 207, 'Santa Fe': 206, 'Sonata': 205, 'Tucson': 204, 'Elantra': 203, 'Kona': 202,
                         'Accent': 201, 'Venue': 200,},
        'Jeep':         {'Gladiator': 216, 'Grand Wagoneer': 215, 'Wrangler': 214, 'Grand Cherokee': 213, 'Cherokee': 212, 
                         'Compass': 211, 'Renegade': 210,},
        'Kia':          {'Telluride': 227, 'K900': 226, 'Stinger': 225, 'Sorento': 224, 'Sportage': 223, 'Forte': 222, 
                         'Soul': 221, 'Rio': 220,},
        'Lexus':        {'LX': 237, 'LS': 236, 'LC': 235, 'GX': 234, 'RX': 233, 'NX': 232, 'ES': 231, 'UX': 230,},
        'Mazda':        {'CX-9': 244, 'MX-5 Miata': 243, 'CX-5': 242, 'Mazda6': 241, 'Mazda3': 240,},
        'Merceds-Benz': {'S-Class': 257, 'G-Class': 256, 'E-Class': 255, 'GLS': 254, 'C-Class': 253, 'GLC': 252,
                         'A-Class': 251, 'CLA-Class': 250,},
        'Nissan':       {'GT-R': 269, 'Armada': 268, 'Titan': 267, 'Pathfinder': 266, 'Murano': 265, 'Rogue': 264, 
                         'Maxima': 263, 'Altima': 262, 'Sentra': 261, 'Versa': 260,},
        'Porsche':      {'911': 276, 'Taycan': 275, 'Panamera': 274, 'Cayenne': 273, 'Macan': 272, '718 Boxster': 271,
                         '718 Cayman': 270,},
        'Subaru':       {'Ascent': 286, 'Outback': 285, 'Forester': 284, 'Crosstrek': 283, 'Legacy': 282, 'Impreza': 281,
                         'WRX': 280,},
        'Tesla':        {'Model S': 293, 'Model X': 292, 'Model 3': 291, 'Model Y': 290,},
        'Toyota':       {'Seqoia': 309, 'Tundra': 308, '4runner': 307, 'Tacoma': 306, 'Avalon': 305,'Highlander': 304, 
                         'RAV4': 303, 'Camry': 302, 'Corolla': 301, 'Prius': 300,},
        'Volkwagen':    {'Touareg': 317, 'Arteon': 316, 'Atlas': 315, 'Passat': 314, 'Tiguan': 313, 'Golf': 312,
                         'Jetta': 311, 'ID.4': 310,},
        'Volvo':        {'XC90': 327, 'XC60': 326, 'S90': 325, 'V90 Cross Country': 324, 'XC40': 323, 'S60': 322, 
                         'V60 Cross Country': 321, 'V60': 320,},
    })

    condition_map = {
        'Poor': 1,
        'Fair': 2,
        'Good': 3,
        'Great': 4,
        'Excellent': 5,
        'Like New': 6,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        if getattr(sys, 'frozen', False):  # If running as a compiled bundle
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath('.')
        
        # Load ONNX model
        model_path = os.path.join(base_path, 'car_value_xgb_regressor.onnx')
        self.session = ort.InferenceSession(model_path)
        self.slider_value = '0'



    def update_model_spinner(self, manufacturer):
        model_spinner = self.ids.model_spinner
        model_spinner.values = list(self.model_map.get(manufacturer, {}).keys())
        model_spinner.text = 'Select model'
        self.model = ''

    def on_year_input(self, year_text):
        try:
            input_year = int(year_text)
            if 1990 <= input_year <= 2024:
                self.year = input_year
            else:
                self.year = 0
        except ValueError:
            self.year = 0

    def on_miles_input(self, miles_text):
        try:
            input_miles = int(miles_text)
            if 0 <= input_miles <= 800000:
                self.miles = input_miles
            else:
                self.miles = 0
        except:
            self.miles = 0

    def submit(self):
        # Convert categorical inputs to integers according to mappings
        make_num = self.make_map.get(self.make, 0)
        model_num = self.model_map.get(self.make, {}).get(self.model, 0)
        condition_num = self.condition_map.get(self.condition, 0)

        input_data = np.array(
            [[(make_num), (model_num), (self.year), (self.miles), (condition_num)]],
            dtype=np.float32
            )

        # Run model
        inputs = {self.session.get_inputs()[0].name: input_data}
        outputs = self.session.run(None, inputs)
        prediction = outputs[0][0]

        self.ids.output_label.text = (
            f"The estimated value of a {self.year} {self.make} {self.model}\n"
            f"with {int(round(self.miles, -3))} miles in {str(self.condition).lower()} condition\n"
            f"is ${float(prediction):.2f}."
        )


    def export_estimate(self):
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserIconView(dirselect=True)
        content.add_widget(filechooser)

        filename_input = TextInput(hint_text='Enter filename', multiline=False, size_hint_y=None, height=30)
        content.add_widget(filename_input)

        save_button = Button(text='Save', size_hint_y=None, height=50)
        content.add_widget(save_button)
        popup = Popup(title='Save Estimate', content=content, size_hint=(0.75, 0.75))

        def save_file(instance):
            selected = filechooser.selection
            print(f"Selected: {selected}")
            if selected and filename_input.text:
                file_path = selected[0]
                print(f"Initial file path: {file_path}")
                if os.path.isdir(file_path):
                    file_path = os.path.join(file_path, filename_input.text)
                else:
                    file_path = selected[0]
                if not file_path.endswith('.txt'):
                    file_path += '.txt'
                print(f"Final file path: {file_path}")

                try:
                    with open(file_path, 'w') as file:
                        file.write("Vehicle Valuation Report\n")
                        file.write(f"Generated: {date.today()}\n\n\n")
                        file.write(self.ids.output_label.text)
                        file.write(f"\n\n\nThis valuation is only an estimate that could differ from\n")
                        file.write(f"actual value and change significantly with time and usage.\n")


                    print(f"File saved: {file_path}")
                except Exception as e:
                    print(f"Failed to save file: {e}")

                popup.dismiss()

        save_button.bind(on_release=save_file)
        popup.open()


class KvCarValueApp(App):
    def build(self):
        return MyLayout()
    
if __name__ == '__main__':
    KvCarValueApp().run()