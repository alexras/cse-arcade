#!/usr/bin/env python

import pygtk
pygtk.require("2.0")
import gtk

import os
import sqlite3
import time

from FrontendConfig import FrontendConfig

### Constants ###
# Emulator/Game model row entries.
NAME = 0
DATA = 1

# So that I don't have to remember how to retrieve the currently
# selected item from a list view (emulator_view/game_view).
def get_selection(view):
    return view.get_cursor()[0][0]

def set_selection(view, value):
    view.set_cursor((value,))

def move_cursor(view, direction):
    selection = get_selection(view)
    selection += direction
    
    if selection < 0:
        selection = 0
    if selection >= len(view.get_model()):
        selection = len(view.get_model()) - 1

    view.set_cursor((selection,))

class Frontend(object):
    # Clean up and exit.
    def exit(self, window):
        self.db.close()
        if self.config['HidePointer']:
            os.system('kill -9 %d' % self.unclutter_child)
        if self.config['IdleKiller']:
            os.system('kill -9 %d' % self.idle_child)

        print 'Goodbye!'
        gtk.main_quit()

    # Launch a game!
    def launch(self, emulator, game):
        launch_string = emulator['path']

        # Hack to make switching interfaces work.
        if game['name'] == 'PyGTK interface' or game['name'] == 'PyGame interface':
            # The pygame interface isn't ready for prime-time yet.
            if game['name'] == 'PyGame interface':
                self.set_description('DISABLED: Not finished yet!')
                return
            if game['name'] == 'PyGTK interface':
                return

            # If we're switching interfaces, replace the executing image.
            print (self.config['RootDir'] + game['path'])
            self.db.commit()
            self.db.close()

            if self.config['HidePointer']:
                os.system('kill -9 %d' % self.unclutter_child)
            if self.config['IdleKiller']:
                os.system('kill -9 %d' % self.idle_child)

            os.execlp('python', 'python', self.config['RootDir'] + game['path'])
            return
        
        if game['args'] is None or game['args'] == '':
            launch_string += ' ' + emulator['args']
        else:
            launch_string += ' ' + game['args']

        if game['path'] is not None:
            launch_string += ' ' + game['path']

        if self.config['Launch']:
            begin_time = time.time()
            os.system(launch_string)
            end_time = time.time()

            time_difference = int(end_time - begin_time)

            cursor = get_selection(self.view)

            update_values = (game['plays'] + 1, game['total_time'] + time_difference, game['id'])
            self.db.execute('update Games set plays = ?, total_time = ? where id == ?', update_values)
            self.db.commit()

            insert_values = (game['id'], int(begin_time), int(end_time))
            self.db.execute('insert into Plays values (?, ?, ?)', insert_values)
            self.db.commit()

            self.repopulate_games(emulator)

            set_selection(self.view, cursor)
        else:
            print launch_string

    # Repopulates the game_{view,model} when a new emulator is selected.
    def repopulate_games(self, emulator):
        self.game_model.clear()

        values = (emulator['id'],)

        for row in self.db.execute('select * from Games where emulator = ? order by name', values):
            self.game_model.append([row['name'], row])

    # Update the selection for non-standard (non-arrow) movement keys.
    def key_press(self, window, event):
        key = gtk.gdk.keyval_name(event.keyval)

        if self.config['PrintKeys']:
            print key

        if key in self.config['UP'] - set(['Up']):
            move_cursor(self.selected_view, -1)

        if key in self.config['DOWN'] - set(['Down']):
            move_cursor(self.selected_view, 1)

    # Handles key events.  Use release rather than press to allow
    # {emulator,game}_view to update its selection before detecting the event.
    def key_release(self, window, event):
        emulator = self.emulator_model[get_selection(self.emulator_view)][DATA]

        key = gtk.gdk.keyval_name(event.keyval)

        if key in self.config['LEFT']:
            self.emulator_view.grab_focus()
            self.selected_view = self.emulator_view
            self.focus = 'Left'
            self.update_info(emulator)
        if key in self.config['RIGHT']:
            game = self.game_model[get_selection(self.game_view)][DATA]

            self.game_view.grab_focus()
            self.selected_view = self.game_view
            self.focus = 'Right'
            self.update_info(game)
        if key in self.config['UP'] or key in self.config['DOWN']:
            if self.focus == 'Left':
                self.repopulate_games(emulator)
                self.game_view.set_cursor(0)
                self.update_info(emulator)
            if self.focus == 'Right':
                game = self.game_model[get_selection(self.game_view)][DATA]
                self.update_info(game)
        if key in self.config['GO']:
            game = self.game_model[get_selection(self.game_view)][DATA]
            self.launch(emulator, game)

    # Updates the preview image and description when given a DB row.
    def update_info(self, item):
        self.set_description(item['description'])
        self.set_preview(self.config['DataDir'] + '/' + item['image'], item['image_height'], item['image_width'])

    # Sets the text under the image.
    def set_description(self, text):
        self.description.set_markup('<span size="18000">%s</span>' % text)

    # Try to set the preview image according to DB info.
    # If unsuccessful (image doesn't exist), fall back to a "not found" image.
    def set_preview(self, path, height, width):
        try:
            self.preview.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(path).scale_simple(width,height,gtk.gdk.INTERP_BILINEAR))
        except:
            self.preview.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file('%s/no_preview.png' % self.config['DataDir']).scale_simple(720,540,gtk.gdk.INTERP_BILINEAR))

    def __init__(self):
        self.config = FrontendConfig('frontend-pygtk')

        # Set default volume levels.
        os.system('amixer set Master 40%')
        os.system('amixer set PCM 100%')

        # Hack because glade won't let me specify a python object type. >:(
        os.system('sed -i -e "s/GObject/PyObject/g" ' + self.config['BaseDir'] + '/Frontend-pygtk.glade')

        # Spawn an unclutter process to hide the mouse pointer.
        if self.config['HidePointer']:
            self.unclutter_child = os.fork()
            if self.unclutter_child == 0:
                while (True):
                    os.system('unclutter')

        if self.config['IdleKiller']:
            self.idle_child = os.fork()
            if self.idle_child == 0:
                while (True):
                    os.system(self.config['RootDir'] + '/Scripts/IdleKiller.py')

        # Get glade objects and connect signal handlers.
        signal_handlers = { 'on_top_level_window_destroy' : self.exit,
                            'on_top_level_window_key_press_event' : self.key_press,
                            'on_top_level_window_key_release_event' : self.key_release }
        builder = gtk.Builder()
        builder.add_from_file('%s/Frontend-pygtk.glade' % self.config['BaseDir'])
        builder.connect_signals(signal_handlers)

        # Get references to important Gtk objects.
        self.top_level_window = builder.get_object('top_level_window')
        self.emulator_view = builder.get_object('emulator_view')
        self.emulator_model = self.emulator_view.get_model()
        self.game_view = builder.get_object('game_view')
        self.game_model = self.game_view.get_model()
        self.preview = builder.get_object('preview_image')
        self.description = builder.get_object('description_label')

        # "Connect" to the sqlite DB and populate the emulator model.
        self.db = sqlite3.connect('%s/Arcade.db' % self.config['DataDir'])
        self.db.row_factory = sqlite3.Row
        for row in self.db.execute('select * from Emulators order by name'):
            self.emulator_model.append([row['name'], row])

        # Init various viewable objects to sane values.
        self.description.set_size_request(600, 200)
        self.description.set_use_markup(True)
        self.description.set_line_wrap(True)
        self.emulator_view.grab_focus()
        self.selected_view = self.emulator_view
        self.emulator_view.set_cursor(0)
        self.repopulate_games(self.emulator_model[0][DATA])
        self.update_info(self.emulator_model[0][DATA])
        self.focus = 'Left'
        self.game_view.set_cursor(0)

        if self.config['Fullscreen']:
            self.top_level_window.fullscreen()
        self.top_level_window.show()

if __name__ == '__main__':
    arcade = Frontend()
    gtk.main()
