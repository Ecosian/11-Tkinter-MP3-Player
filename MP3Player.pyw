from tkinter import *
import tkinter.filedialog as filedialog
import tkinter.messagebox as msgbox
import pygame
import pygame.mixer as player
import os
import time
from mutagen.mp3 import MP3
import tkinter as tk

_BG_COLOR = 'pink'
_FG_COLOR = 'black'
_FG_ALT_COLOR = 'black'
_LOOP_OFF = 'off'
_LOOP_ON = 'on'
_LOOP_ONCE = 'once'

#creating tooltip for button or styledbuttons.
class tool_tip(object):
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     
        self.wraplength = 180   
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 15
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='center',
                       background="yellow", relief='flat', borderwidth=0,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()

class StyledFrame(Frame):
    def __init__(self, master, **kwargs):
        kwargs['bg'] = _BG_COLOR
        super(StyledFrame, self).__init__(master, **kwargs)

class StyledButton(Button):
    def __init__(self, master, **kwargs):
        kwargs['bg'] = _BG_COLOR
        kwargs['fg'] = _FG_COLOR
        kwargs['relief'] = FLAT
        kwargs['activebackground'] = _FG_COLOR
        kwargs['activeforeground'] = _FG_ALT_COLOR
        kwargs['bd'] = 0
        super(StyledButton, self).__init__(master, **kwargs)

class SettingsMenu(StyledFrame):
    def __init__(self, master):
        super(SettingsMenu, self).__init__(master)
        self.mp3 = master
        self.loop_setting = _LOOP_OFF
        self.shuffle_setting = False
        self.create_images()
        self.create_widgets()

    def create_images(self):
        self.loop_off_img = PhotoImage(file='loop_off.png')
        self.loop_on_img = PhotoImage(file='loop_on.png')
        self.loop_once_on_img = PhotoImage(file='loop_once_on.png')
        self.loop_once_off_img = PhotoImage(file='loop_once_off.png')
        self.shuffle_off_img = PhotoImage(file='shuffle_off.png')
        self.shuffle_on_img  = PhotoImage(file='shuffle_on.png')
        self.add_img = PhotoImage(file='add.png')

    def create_widgets(self):
        self.loopButton = StyledButton(self, image=self.loop_off_img,
                                       command=self.loop)
        self.looponceButton = StyledButton(self, image=self.loop_once_off_img,
                                           command=self.loop_once)
        self.shuffleButton = StyledButton(self, image=self.shuffle_off_img,
                                          command=self.shuffle)
        self.addButton = StyledButton(self, image=self.add_img,
                                      command=self.add)
        self.loopButton.pack(side=LEFT)
        self.looponceButton.pack(side=LEFT)
        self.shuffleButton.pack(side=LEFT)
        self.addButton.pack(side=RIGHT)

        self.loopButtontip = tool_tip(self.loopButton, 'Each MP3 File(s) will be played over and over again')
        self.looponceButtontip = tool_tip(self.looponceButton, 'Each MP3 File(s) will be played twice')
        self.shuffleButtontip = tool_tip(self.shuffleButton, 'MP3 Files will be shuffled(randomly played)')
        self.addButtontip = tool_tip(self.addButton,'Add MP3 File(s)')

    def loop(self):
        if self.loop_setting is _LOOP_OFF:
            self.loop_setting = _LOOP_ON
            self.loopButton.config(image=self.loop_on_img)
        elif self.loop_setting is _LOOP_ON:
            self.loop_setting = _LOOP_OFF
            self.loopButton.config(image=self.loop_off_img)

    def loop_once(self):
            if self.loop_setting is _LOOP_OFF:
                self.loop_setting = _LOOP_ONCE
                self.looponceButton.config(image=self.loop_once_on_img)
                player.music.play(1,0.0)
            elif self.loop_setting is _LOOP_ONCE:
                self.loop_setting = _LOOP_OFF
                self.looponceButton.config(image=self.loop_once_off_img)
                
    def shuffle(self):
        self.shuffle_setting = not self.shuffle_setting
        if self.shuffle_setting:
            self.shuffleButton.config(image=self.shuffle_on_img)
        else:
            self.shuffleButton.config(image=self.shuffle_off_img)

    def add(self):
        files = filedialog.askopenfilename(initialdir= "/", title="Select an MP3(.mp3) File", defaultextension = '.mp3', filetypes = [('MP3', '.mp3'),])    
        song_list = list(self.mp3.master.splitlist(files))
        for song_path in song_list:
            self.mp3.playlist.append(song_path);
            split_path = song_path.split('/')
            song_name = split_path[-1][:-4]
            self.mp3.playlistbox.insert(END, song_name)

class ControlBar(StyledFrame):
    def __init__(self, master):
        super(ControlBar, self).__init__(master)
        self.mp3 = master
        self.playing = False
        self.create_images()
        self.create_widgets()

    def create_images(self):
        self.prev_img = PhotoImage(file='previous.png')
        self.stop_img = PhotoImage(file='stop.png')
        self.play_img = PhotoImage(file='play.png')
        self.pause_img = PhotoImage(file='pause.png')
        self.next_img = PhotoImage(file='next.png')

    def create_widgets(self):
        self.prevButton = StyledButton(self, image=self.prev_img,
                                      command=self.prev)
        self.stopButton = StyledButton(self, image=self.stop_img,
                                      command=self.stop)
        self.playButton = StyledButton(self, image=self.play_img,
                                      command=self.play_pause_wrapper)
        self.nextButton = StyledButton(self, image=self.next_img,
                                      command=self.next)
        buttons = [self.prevButton, self.stopButton,
                   self.playButton, self.nextButton]
        for button in buttons:
            button.pack(side=LEFT)

        self.prevButtontip = tool_tip(self.prevButton, 'Previous MP3 file will be played')
        self.stopButtontip = tool_tip(self.stopButton, 'Stop Playing')
        self.playButtontip = tool_tip(self.playButton, 'Start/Pause Playing')
        self.nextButtontip = tool_tip(self.nextButton, 'Next MP3 file will be played')

    def play_pause_wrapper(self):
        self.playing = not self.playing
        if self.playing:
            self.playButton.config(image=self.pause_img)
        else:
            self.playButton.config(image=self.play_img)
        self.play()

    def play(self):
        if self.mp3.playlistbox.size() == 0:
            msgbox.showwarning('Playlist Empty', 'Add songs to your playlist!')
        else:
            player.music.stop()
            current_selection = (self.get_current_song() or 0)
            song_to_play = self.mp3.playlist[current_selection]
            player.music.load(song_to_play)
            player.music.play(0, 0.0)

    def prev(self):
        current_selection = self.get_current_song()
        if current_selection - 1 >= 0:
            self.mp3.playlistbox.selection_clear(current_selection)
            self.mp3.playlistbox.selection_set(current_selection - 1)
            self.play()

    def next(self):
        current_selection = self.get_current_song()
        if current_selection + 1 < self.mp3.playlistbox.size():
            self.mp3.playlistbox.selection_clear(current_selection)
            self.mp3.playlistbox.selection_set(current_selection + 1)
            self.play()
        else:
            self.mp3.playlistbox.selection_clear(current_selection)
            self.mp3.playlistbox.selection_set(0)
            self.play()

    def stop(self):
        player.music.stop()

    def get_current_song(self):
        try:
            return self.mp3.playlistbox.curselection()[0]
        except:
            if self.mp3.playlistbox.size() > 0:
                self.mp3.playlistbox.selection_set(0)
            return 0

class VolumeControls(StyledFrame):
    def __init__(self, master):
        super(VolumeControls, self).__init__(master)
        self.mp3 = master
        self.create_images()
        self.create_widgets()
        self.volume.set(100)

    def create_images(self):
        self.vol_off_img = PhotoImage(file='speaker_down.png')
        self.vol_on_img = PhotoImage(file='speaker_up.png')

    def create_widgets(self):
        self.vol_off = Label(self, image=self.vol_off_img, bg=_BG_COLOR)
        self.volume = Scale(self, bd=0, bg=_FG_COLOR,
                            highlightthickness=2, highlightcolor=_BG_COLOR,
                            highlightbackground=_FG_COLOR,
                            activebackground=_BG_COLOR,
                            troughcolor=_BG_COLOR,
                            from_=0, to=100, orient=HORIZONTAL,
                            showvalue=False,
                            sliderrelief=FLAT, sliderlength=10,
                            command=self.change_volume)
        self.vol_on  = Label(self, image=self.vol_on_img, bg=_BG_COLOR)
        self.vol_off.pack(side=LEFT)
        self.volume.pack(side=LEFT)
        self.vol_on.pack(side=LEFT)

        self.vol_off_tip = tool_tip(self.vol_off, 'Mute the Volume')
        self.volume_tip = tool_tip(self.volume, 'Increase/Decrease te Volume')
        self.vol_on_tip = tool_tip(self.vol_on, 'Unmute the Volume')
        
    def change_volume(self, event):
        pass

class SimpleMP3(StyledFrame):
    def __init__(self, master):
        super(SimpleMP3, self).__init__(master)
        self.master = master
        self.playlist = []
        self.master.config(bg=_BG_COLOR, padx=2, pady=2)
        self.create_widgets()
        self.pack()
        pygame.init()

    def create_widgets(self):
        self.settings_bar = SettingsMenu(self)
        self.settings_bar.pack(side=TOP, fill=X)
        self.playlistframe = StyledFrame(self)
        self.scrollbar = Scrollbar(self.playlistframe,
                                   activerelief=FLAT, relief=FLAT)
        self.playlistbox = Listbox(self.playlistframe, width=50,
                                   fg=_FG_COLOR, bg=_BG_COLOR,relief=FLAT,
                                   borderwidth=2, highlightthickness=0,
                                   activestyle='none',
                                   selectforeground=_FG_ALT_COLOR,
                                   selectbackground=_BG_COLOR,
                                   selectmode=SINGLE)
        for song in self.playlist:
            self.playlistbox.insert(END, song)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.playlistbox.pack(side=TOP, fill=BOTH, pady=2, padx=2)
        self.playlistbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.playlistbox.yview)
        self.playlistframe.pack(side=TOP, fill=BOTH)
        self.volume_bar = VolumeControls(self)
        self.volume_bar.pack(side=TOP, expand=True, fill='none')
        self.control_bar = ControlBar(self)
        self.control_bar.pack(expand=True, fill='none')

def main():
    gui = Tk()
    gui.title('MP3 Player')
    gui.iconbitmap('player.ico')
    gui.geometry('300x243+500+0')
    application = SimpleMP3(gui)
    application.mainloop()

if __name__ == '__main__':
    main()
