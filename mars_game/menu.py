#Imports
import subprocess

from customtkinter import *
#making class
class Menu(CTk):
    def __init__(self):
        super().__init__()
        #Window settings
        self.geometry("640x480")
        self.title("Mars Defense")
        self.resizable(False, False)

        #making frames
        self.main_menu = CTkFrame(self, fg_color="#eb8934", width=640, height=480)
        self.main_menu.place(x=0, y=0)
        self.settings_menu = CTkFrame(self, fg_color="#eb8934", width=640, height=480)

        #Variables
        self.music_state = "On"
        self.fullscreen_state = "Off"
        self.music_volume = 50
        self.sound_effects_volume = 50

        #making widgets for main_menu
        self.game_name_label = CTkLabel(self. main_menu, text="Mars Defense", font=("Orbitron", 70, "bold"))
        self.game_name_label.place(x=125,  y=50)

        self.start_button = CTkButton(self.main_menu, text="Start", font=("Orbitron", 50, "bold"), fg_color="#3A2418", border_width=0, command=self.launch_game)
        self.start_button.place(x=250, y=150)

        self.settings_button = CTkButton(self.main_menu, text="Settings", font=("Orbitron", 50, "bold"), fg_color="#3A2418", command=self.show_settings_menu)
        self.settings_button.place(x=215, y=250)

        self.quit_button = CTkButton(self.main_menu, text="Quit", font=("Orbitron", 50, "bold"), fg_color="#3A2418", command=self.quit_game)
        self.quit_button.place(x=250, y=350)

        #making widgets for settings_menu
        self.back_button = CTkButton(self.settings_menu, text="Back", font=("Orbitron", 50, "bold"), fg_color="#3A2418", border_width=0, command=self.show_main_menu)
        self.back_button.place(x=25, y=400)

        self.music_checkbox = CTkCheckBox(self.settings_menu, text="Toggle music", text_color="#3A2418", fg_color="#3A2418", font=("Orbitron", 50, "bold"), command=self.toggle_music)
        self.music_checkbox.place(x=125, y=100)
        self.music_checkbox.select()

        self.volume_label = CTkLabel(self.settings_menu, text="Music volume: 50%", width=200, height=50, text_color="#3A2418", font=("Orbitron", 50, "bold"))
        self.volume_label.place(x=125, y=190)

        self.volume_slider = CTkSlider(self.settings_menu, from_=0, to=100, button_color="#3A2418", progress_color="#3A2418", command=self.update_volume_label)
        self.volume_slider.place(x=125, y=250)
        self.volume_slider.set(50)

        self.sound_effects_volume_slider = CTkSlider(self.settings_menu, from_=0, to=100, button_color="#3A2418", progress_color="#3A2418", command=self.update_sound_effects_volume_label)
        self.sound_effects_volume_slider.place(x=125, y=375)
        self.sound_effects_volume_slider.set(50)

        self.sound_effects_volume_label = CTkLabel(self.settings_menu, text="SFX volume: 50%", width=200, height=50, text_color="#3A2418", font=("Orbitron", 50, "bold"))
        self.sound_effects_volume_label.place(x=125, y=300)


    #making functions
    def show_settings_menu(self):
        self.main_menu.place_forget()
        self.settings_menu.place(x=0, y=0)

    def show_main_menu(self):
        self.settings_menu.place_forget()
        self.main_menu.place(x=0, y=0)

    def quit_game(self):
        self.destroy()

    def toggle_music(self):
        if self.music_state == "On":
            self.music_state = "Off"
        else:
            self.music_state = "On"

    def update_volume_label(self, value):
        self.music_volume = int(value)
        self.volume_label.configure(text=f"Music volume: {int(value)}%")

    def update_sound_effects_volume_label(self, value):
        self.sound_effects_volume = int(value)
        self.sound_effects_volume_label.configure(text=f"SFX volume: {int(value)}%")

    def launch_game(self):
        music_volume = str(self.music_volume)
        music_state = self.music_state
        sound_effects_volume = str(self.sound_effects_volume)
        self.destroy()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        game_path = os.path.join(script_dir, "game.py")

        subprocess.run([
            sys.executable,
            game_path,
            music_state,
            music_volume,
            sound_effects_volume
        ])



menu = Menu()
menu.mainloop()