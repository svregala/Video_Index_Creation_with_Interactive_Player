import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import pygame.time
from pygame import mixer
from IndexCreation import CreateIndex
import sys

class MyVideoCapture:
   def __init__(self, video_source):
      # Open the video source
      self.vid = cv2.VideoCapture(video_source)
      if not self.vid.isOpened():
         raise ValueError("Unable to open the video source", video_source)

      # Get video source width and height
      self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
      self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

   def get_frame(self):
      if self.vid.isOpened():
         ret, frame = self.vid.read()
         if ret:
               # Return a boolean success flag and the current frame converted to BG
               return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
         else:
               return (ret, None)

   def __del__(self):
      if self.vid.isOpened():
         self.vid.release()

   def set_frame(self, frame_ind):
      self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_ind - 1)

   def get_audio(self, vid_fps, frameNum):
      #return (self.vid.get(cv2.CAP_PROP_POS_FRAMES)-1)/ vid_fps
      return frameNum/vid_fps
   
   def get_photos(self):
      photos = []

      while self.vid.isOpened():
         ret, frame = self.vid.read()

         if ret:
               frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
               photo = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(frame))
               photos.append(photo)

         else:
               break

      return photos


class MyAudioCapture:
   def __init__(self, audio_source):
      mixer.init()
      mixer.music.load(audio_source)

   def get_audio(self, vid_fps, frameNum):
      #return (self.vid.get(cv2.CAP_PROP_POS_FRAMES)-1)/ vid_fps
      return frameNum/vid_fps
   

# Store the table of contents (toc) buttons in a dictionary
# We need a unique key to represent every button - when a button's frame is played, how can we map this frame back to
# button ??? Are the frame numbers behind all buttons unique?
selected_button = None
selected_scene_button = None
selected_shot_button = None
selected_SUBshot_button = None
toc_scene_buttons = {}
toc_shot_buttons = {}
toc_SUBshot_buttons = {}

map_shot_to_scene = {}
map_SUBshot_to_shot = {}
   

'''Class inherits from tkinter.Frame so that it can create a container for 
the Canvas and Scrollbar widgets, and manage their layout.'''
class ScrollableList(tkinter.Frame):
   def __init__(self, master, vid_play_instance, scene_arr, shot_arr, subshot_arr):
      '''calls the constructor of the parent class (tkinter.Frame) with the same arguments (master). 
      This is necessary to initialize the ScrollableList object as an instance of the tkinter.Frame class, 
      and to ensure that it has all the attributes and methods of its parent class.'''
      super().__init__(master)
      self.video_player_instance = vid_play_instance

      # Create the canvas and scrollbar widgets
      # Creates an additional Canvas widget that will be used to hold the Frame that will contain the buttons
      ''' we want to be able to scroll the Frame (containing the buttons) independently of the parent window. 
      In order to achieve this, we create a separate Canvas widget and set it up with a scrollbar, 
      then pack the Frame containing the buttons inside the Canvas widget.'''
      self.canvas_indexes = tkinter.Canvas(self, width=400, height=600, highlightbackground='blue', highlightcolor='blue', highlightthickness=1)
      scrollbar = tkinter.Scrollbar(self, orient='vertical', command=self.canvas_indexes.yview)
      self.canvas_indexes.config(yscrollcommand=scrollbar.set)

      # Create a label widget for the movie name
      text_label = tkinter.Label(self.canvas_indexes, text="INSERT MOVIE NAME", font=("Arial", 14))
      # Add the label widget to the canvas
      self.canvas_indexes.create_window((20, 0), window=text_label, anchor='center')

      # Create a frame inside the canvas to hold the buttons
      self.button_frame = tkinter.Frame(self.canvas_indexes, bg="white", width=400, height=600)

      # Convert scene and shot arrays into sets for element checking
      scene_SET = set(scene_arr)
      shot_SET = set(shot_arr)

      row_count = 1
      curr_shot_idx = 0
      curr_SUBshot_idx = 0
      # Outer for-loop: ADD SCENE BUTTONS
      for i in range(len(scene_arr)):
         parent_scene_button = self.create_scene_button(i, row_count, scene_arr[i])
         row_count += 1

         # Add the button to the toc_scene_buttons dictionary
         # toc_scene_buttons[scene_arr[i]] = self.jump_scene

         name_shot_count = 1
         count_shot_added = 0
         for j in range(curr_shot_idx, len(shot_arr)):
            # Check index out of range - enter if statement if we are NOT at the last element
            if j+1 < len(shot_arr):
               if shot_arr[j+1] in scene_SET:
                  if count_shot_added == 0:
                     curr_shot_idx += 1 # NEW EDIT MADE HERE
                     # NEW EDIT MADE HERE
                     if subshot_arr[curr_SUBshot_idx] in scene_SET:
                        curr_SUBshot_idx += 1
                     while subshot_arr[curr_SUBshot_idx] not in scene_SET:
                        curr_SUBshot_idx += 1
                     break
                  else:
                     # This takes care of when we've added shot buttons and we've reached the LAST element to be added
                     # in this sequence, before moving on to the next scene frame
                     parent_shot = self.create_shot_button(j, row_count, shot_arr[j], name_shot_count, parent_scene_button)

                     curr_shot_idx += 1
                     row_count += 1

                     # HERE HERE ------
                     # Add the button to the toc_shot_buttons dictionary
                     #toc_shot_buttons[shot_arr[j]] = self.jump_shot
                     
                     name_SUBshot_count = 1
                     count_SUBshot_added = 0
                     for x in range(curr_SUBshot_idx, len(subshot_arr)):
                        if x+1 < len(subshot_arr):
                           if subshot_arr[x+1] in shot_SET:
                              if count_SUBshot_added == 0:
                                 curr_SUBshot_idx += 1 # NEW EDIT MADE HERE
                                 break
                              else:
                                 self.create_SUBshot_button(x, row_count, subshot_arr[x], name_SUBshot_count, parent_shot)

                                 curr_SUBshot_idx += 1
                                 row_count += 1
                                 break

                           curr_SUBshot_idx += 1
                           self.create_SUBshot_button(x, row_count, subshot_arr[x], name_SUBshot_count, parent_shot)

                           name_SUBshot_count += 1
                           row_count += 1
                           count_SUBshot_added += 1

                        else:
                           if subshot_arr[x] not in shot_SET:
                              curr_SUBshot_idx += 1
                              self.create_SUBshot_button(x, row_count, subshot_arr[x], name_SUBshot_count, parent_shot)

                              name_SUBshot_count += 1
                              row_count += 1
            
                     # HERE HERE ------
                     break # FIND ANOTHER SOLUTION TO THIS BECAUSE WE WANT TO EXECUTE THE FOLLOWING FORLOOP AFTER ANY SORT OF BREAK

               curr_shot_idx += 1
               parent_shot = self.create_shot_button(j, row_count, shot_arr[j], name_shot_count, parent_scene_button)

               name_shot_count += 1
               row_count += 1
               count_shot_added += 1

               # HERE HERE ------
               # Add the button to the toc_shot_buttons dictionary
               #toc_shot_buttons[shot_arr[j]] = self.jump_shot
               
               name_SUBshot_count = 1
               count_SUBshot_added = 0
               for x in range(curr_SUBshot_idx, len(subshot_arr)):
                  if x+1 < len(subshot_arr):
                     if subshot_arr[x+1] in shot_SET:
                        if count_SUBshot_added == 0:
                           curr_SUBshot_idx += 1 # NEW EDIT MADE HERE
                           break
                        else:
                           self.create_SUBshot_button(x, row_count, subshot_arr[x], name_SUBshot_count, parent_shot)

                           curr_SUBshot_idx += 1
                           row_count += 1
                           break

                     curr_SUBshot_idx += 1
                     self.create_SUBshot_button(x, row_count, subshot_arr[x], name_SUBshot_count, parent_shot)

                     name_SUBshot_count += 1
                     row_count += 1
                     count_SUBshot_added += 1

                  else:
                     if subshot_arr[x] not in shot_SET:
                        curr_SUBshot_idx += 1
                        self.create_SUBshot_button(x, row_count, subshot_arr[x], name_SUBshot_count, parent_shot)

                        name_SUBshot_count += 1
                        row_count += 1
               # HERE HERE ------
               # -----------------------------

            # Enter else if we ARE the last element
            else:
               if shot_arr[j] not in scene_SET:
                  curr_shot_idx += 1

                  # Add shot if current shot element is not greater than the next i element
                  parent_shot = self.create_shot_button(j, row_count, shot_arr[j], name_shot_count, parent_scene_button)

                  name_shot_count += 1
                  row_count += 1

                  # HERE HERE ------
                  # Add the button to the toc_shot_buttons dictionary
                  #toc_shot_buttons[shot_arr[j]] = self.jump_shot
                  
                  name_SUBshot_count = 1
                  count_SUBshot_added = 0
                  for x in range(curr_SUBshot_idx, len(subshot_arr)):
                     if x+1 < len(subshot_arr):
                        if subshot_arr[x+1] in shot_SET:
                           if count_SUBshot_added == 0:
                              curr_SUBshot_idx += 1 # NEW EDIT MADE HERE
                              break
                           else:
                              self.create_SUBshot_button(x, row_count, subshot_arr[x], name_SUBshot_count, parent_shot)

                              curr_SUBshot_idx += 1
                              row_count += 1
                              break

                        curr_SUBshot_idx += 1
                        self.create_SUBshot_button(x, row_count, subshot_arr[x], name_SUBshot_count, parent_shot)

                        name_SUBshot_count += 1
                        row_count += 1
                        count_SUBshot_added += 1

                     else:
                        if subshot_arr[x] not in shot_SET:
                           curr_SUBshot_idx += 1
                           self.create_SUBshot_button(x, row_count, subshot_arr[x], name_SUBshot_count, parent_shot)

                           name_SUBshot_count += 1
                           row_count += 1

                  # HERE HERE ------
         ###### ----------------------------------------------------------------------------------------------------------------------------------------------------------

      
      # Pack the button frame inside the canvas
      self.canvas_indexes.create_window((0, 30), window=self.button_frame, anchor='nw')

      # Configure the canvas and scrollbar
      self.canvas_indexes.config(scrollregion=self.canvas_indexes.bbox('all'))
      self.canvas_indexes.bind_all('<MouseWheel>', self.mouse_scroll)
      scrollbar.pack(side='right', fill='y')
      self.canvas_indexes.pack(side='left', fill='both', expand=True)

   def mouse_scroll(self, event=None):
      """Configure the scrollbar to respond to mouse wheel events"""
      if event.num == 4:
         self.canvas_indexes.yview_scroll(-1, 'units')
      elif event.num == 5:
         self.canvas_indexes.yview_scroll(1, 'units')

   def create_scene_button(self, idx, row_ct, frame_num):
      button_scene = f"Scene {idx+1}"
      #self.jump_scene = tkinter.Button(self.button_frame, text=button_scene, command=self.video_player_instance.create_command(i, scene_arr[i]))
      self.jump_scene = tkinter.Button(self.button_frame, text=button_scene)
      self.jump_scene.config(command=self.video_player_instance.create_command(idx, frame_num, self.jump_scene, "scene"))
      self.jump_scene.grid(row=row_ct, column=0, sticky='w')
      self.jump_scene.configure(highlightbackground="white")
      self.jump_scene.update()
      toc_scene_buttons[frame_num] = self.jump_scene

      return self.jump_scene

   def create_shot_button(self, idx, row_ct, frame_num, name_count, parent):
      button_shot = f"Shot {name_count}"
      #self.jump_shot = tkinter.Button(self.button_frame, text=button_shot, command=self.video_player_instance.create_command(j, shot_arr[j]))
      self.jump_shot = tkinter.Button(self.button_frame, text=button_shot)
      self.jump_shot.config(command=self.video_player_instance.create_command(idx, frame_num, self.jump_shot, "shot"))
      self.jump_shot.grid(row=row_ct, column=1, sticky='w')
      self.jump_shot.configure(highlightbackground="white")
      self.jump_shot.update()
      toc_shot_buttons[frame_num] = self.jump_shot

      # Update map
      map_shot_to_scene[self.jump_shot] = parent
      return self.jump_shot

   def create_SUBshot_button(self, idx, row_ct, frame_num, name_count, parent):
      button_SUBshot = f"Subshot {name_count}"
      #self.jump_SUBshot = tkinter.Button(self.button_frame, text=button_SUBshot, command=self.video_player_instance.create_command(x, subshot_arr[x]))
      self.jump_SUBshot = tkinter.Button(self.button_frame, text=button_SUBshot)
      self.jump_SUBshot.config(command=self.video_player_instance.create_command(idx, frame_num, self.jump_SUBshot, "subshot"))
      self.jump_SUBshot.grid(row=row_ct, column=2, sticky='w')
      self.jump_SUBshot.configure(highlightbackground="white")
      self.jump_SUBshot.update()
      toc_SUBshot_buttons[frame_num] = self.jump_SUBshot

      # Update map
      map_SUBshot_to_shot[self.jump_SUBshot] = parent

class VideoPlayer:
   def __init__(self, window, window_title, video_source, audio_source, scenes, shots, subshots):
      self.window = window
      self.window.geometry('1200x800')
      self.window_title = window_title
      self.video_source = video_source
      self.audio_source = audio_source

      self.scenes = scenes
      self.shots = shots
      self.subshots = subshots

      # Open the video source
      self.vid = MyVideoCapture(video_source)

      # Open the audio source
      self.aud = MyAudioCapture(audio_source)

      # Create a canvas that will contain and display the video
      self.canvas = tkinter.Canvas(window, width=self.vid.width, height=self.vid.height, highlightbackground='red', highlightcolor='red', highlightthickness=1)
      #self.canvas.pack()

      self.photos = self.vid.get_photos()
      
      self.image_on_canvas = self.canvas.create_image(0, 0, image=self.photos[0], anchor=tkinter.NW)
      
      # Create a canvas that will contain the Play and Pause Buttons
      self.canvas_play_pause = tkinter.Canvas(window, width=400, height=100, highlightbackground='red', highlightcolor='red', highlightthickness=1)
      #self.canvas_play_pause.pack()

      # Buttons - Play & Pause & Stop
      self.btn_play = tkinter.Button(window, text="PLAY", command=self.play)
      #self.btn_play.pack(anchor=tkinter.CENTER, expand=True)

      self.btn_pause = tkinter.Button(window, text="PAUSE", command=self.pause)
      #self.btn_pause.pack(anchor=tkinter.CENTER, expand=True)

      self.btn_stop = tkinter.Button(window, text="STOP", command=self.stop)

      self.canvas_play_pause.create_window(50,50, anchor='nw', window=self.btn_play)
      self.canvas_play_pause.create_window(150,50, anchor='nw', window=self.btn_pause)
      self.canvas_play_pause.create_window(250,50, anchor='nw', window=self.btn_stop)

      '''The canvas widget will be used as the parent widget for the ScrollableList widget that is created'''
      self.canv_ind = tkinter.Canvas(window)
      self.list1 = ScrollableList(self.canv_ind, self, scenes, shots, subshots)

      self.canv_ind.grid(row=0, column=0, rowspan=2)
      self.canvas.grid(row=0, column=1, padx=10)
      self.canvas_play_pause.grid(row=1, column=1, padx=10)

      self.list1.grid(row=0, column=0)
      
      # Define the delay (milliseconds) between calls to update() - default to 33
      # self.delay = 33 #24 # 33 Hardcoded values -- LOOK BELOW FOR GENERALIZATION

      # Define a variable to trigger jumping to a different frame     
      self.is_jump = False

      # Define a variable to hold the current frame
      self.current_frame = 1

      # Stop Button logic
      self.current_selected_shot = 0
      self.is_stopped = False

      # Define a variable to hold the current audio position
      self.audio_position = 0
      self.audio_paused = False
      self.video_fps = self.vid.vid.get(cv2.CAP_PROP_FPS) # 30 fps, 24

      # Define the delay (milliseconds) between calls to update() - default to 33
      self.delay = round(1000/self.video_fps)
      # Convert fps to a whole number after calculating the delay
      self.video_fps = round(self.video_fps)

      self.total_audio_time = 0 #in ms 
      self.prev_total_audio_time = 0 #in ms

      self.start_position = 0

      # Define a variable to track the ID of the "after" activity, which repaints the video frames
      self.after_id = None

      # Define a variable to track whether the video (imagery + audio) is playing
      # This prevents side effects of pressing the play button consecutively
      self.is_playing = False
      
      # Define a variable to track the time that the 

      self.window.mainloop()


   '''
   Button handlers
   '''
   def play(self):
      # Play the video
      self.play_video()
      # Play the sound
      self.play_sound()
      # After self.delay ms, this method will call itself again
      self.after_id = self.window.after(self.delay, self.play)


   def pause(self):
      # Pause the video
      self.pause_video()
      # Pause the sound
      self.pause_sound()

   
   def stop(self):
      # Pause the video & audio
      self.pause()
      # Move the current frame back to the last selected shot
      self.current_frame = self.current_selected_shot
      self.is_stopped = True


   def play_video(self):
      """The update method will be recalled every self.delay amount of time"""

      # Read the next frame from the video source
      if self.is_jump:
         #ret, frame = self.vid.get_frame()

         frame_index = self.current_frame
         # Set the position of the video to the desired frame
         #self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_index - 1)
         self.vid.set_frame(frame_index)
         #ret, frame = self.vid.get_frame()

         self.start_position = self.aud.get_audio(self.video_fps, self.current_frame)
         jump_audio_pos = self.aud.get_audio(self.video_fps, self.current_frame)
         # Handle the case for when we jump to a scene and then press play
         if mixer.music.get_pos() == -1:
               mixer.music.play(start=float(jump_audio_pos))
         else:
               pygame.mixer.music.set_pos(float(jump_audio_pos))
               
         self.is_jump = False

      # Set the flag is_playing to True
      self.is_playing = True

      # Stop the timer if we have reached the end of the video
      if self.current_frame >= len(self.photos):
         self.pause()
         return
      
      # If the current frame corresponds to a TOC button, highlight (color) that button
      # If a previous button has been colored, remove its color
      scene_button_to_highlight = None
      shot_button_to_highlight = None
      sub_shot_button_to_highlight = None

      if self.current_frame in toc_scene_buttons:
         scene_button_to_highlight = toc_scene_buttons[self.current_frame]
         # For Stop button
         self.current_selected_shot = self.current_frame
      if self.current_frame in toc_shot_buttons:
         shot_button_to_highlight = toc_shot_buttons[self.current_frame]
         # For Stop button
         self.current_selected_shot = self.current_frame
      if self.current_frame in toc_SUBshot_buttons:
         sub_shot_button_to_highlight = toc_SUBshot_buttons[self.current_frame]
         # For Stop button
         self.current_selected_shot = self.current_frame

      global selected_scene_button
      global selected_shot_button
      global selected_SUBshot_button

      if scene_button_to_highlight:
         if selected_scene_button:
            selected_scene_button.configure(highlightbackground="white")
            #selected_scene_button.configure(default="normal")
         scene_button_to_highlight.configure(highlightbackground="yellow")
         selected_scene_button = scene_button_to_highlight

         # If a shot button is highlighted, this needs to be disabled because we're now transitioning to a new scene
         if selected_shot_button:
            selected_shot_button.configure(highlightbackground="white")

         if selected_SUBshot_button:
            selected_SUBshot_button.configure(highlightbackground="white")
               
      if shot_button_to_highlight:
         if selected_shot_button:
            selected_shot_button.configure(highlightbackground="white")
         shot_button_to_highlight.configure(highlightbackground="orange")
         selected_shot_button = shot_button_to_highlight

         if selected_SUBshot_button:
            selected_SUBshot_button.configure(highlightbackground="white")

      if sub_shot_button_to_highlight:
         if selected_SUBshot_button:
            selected_SUBshot_button.configure(highlightbackground="white")
         sub_shot_button_to_highlight.configure(highlightbackground="red")
         selected_SUBshot_button = sub_shot_button_to_highlight

      #self.canvas.create_image(0, 0, image=self.photos[self.current_frame], anchor=tkinter.NW)
      self.canvas.itemconfig(self.image_on_canvas, image=self.photos[self.current_frame])

      self.current_frame = self.current_frame + 1


   def pause_video(self):
      if self.is_playing:
         self.window.after_cancel(self.after_id)
      
      self.is_playing = False
      

   def play_sound(self):
      if mixer.music.get_pos() == -1 or self.is_stopped:
         mixer.music.play(start=self.aud.get_audio(self.video_fps, self.current_frame))
         self.start_position = self.aud.get_audio(self.video_fps, self.current_frame)
         self.is_stopped = False
      elif self.audio_paused and self.is_playing:
         mixer.music.unpause()
         self.start_position = self.aud.get_audio(self.video_fps, self.current_frame)
         self.audio_paused = False
      else:
         self.total_audio_time = mixer.music.get_pos()

      elapsed_time = abs(self.prev_total_audio_time-self.total_audio_time)

      self.audio_position = elapsed_time + self.start_position
      #print(elapsed_time)

      exp_audio_pos = int(((self.current_frame)/self.video_fps)*1000)
      audio_diff = abs(self.audio_position-exp_audio_pos)

      if (self.current_frame)%(3*self.video_fps) == 0:
         if audio_diff > 500:
               pygame.mixer.music.set_pos(float(exp_audio_pos/1000.0))


   def pause_sound(self):
      mixer.music.pause()
      self.audio_paused = True
      # Set audio position to where we paused it
      #self.audio_position = mixer.music.get_pos()
      #print("current position of the sound:")
      #print(mixer.music.get_pos())

      self.total_audio_time = mixer.music.get_pos()
      self.prev_total_audio_time = self.total_audio_time


   # Define a function for each command
   def create_command(self, i, frame_num, button, type):
      def jump_command():
         global selected_scene_button
         global selected_shot_button
         global selected_SUBshot_button

         if type == "scene":
            if selected_scene_button:
               selected_scene_button.configure(highlightbackground="white")
            button.configure(highlightbackground="yellow")
            selected_scene_button = button

            if selected_shot_button:
               selected_shot_button.configure(highlightbackground="white")

            if selected_SUBshot_button:
               selected_SUBshot_button.configure(highlightbackground="white")

         elif type == "shot":
            if selected_shot_button:
               selected_shot_button.configure(highlightbackground="white")
            button.configure(highlightbackground="orange")
            selected_shot_button = button

            if selected_SUBshot_button:
               selected_SUBshot_button.configure(highlightbackground="white")

            # Find shot button parent and highlight
            parent_scene_button = map_shot_to_scene[selected_shot_button]
            if selected_scene_button:
               selected_scene_button.configure(highlightbackground="white")
            parent_scene_button.configure(highlightbackground="yellow")
            selected_scene_button = parent_scene_button

         else:
            if selected_SUBshot_button:
               selected_SUBshot_button.configure(highlightbackground="white")
            button.configure(highlightbackground="red")
            selected_SUBshot_button = button

            # Find subshot button parent and highlight
            parent_shot_button = map_SUBshot_to_shot[selected_SUBshot_button]
            if selected_shot_button:
               selected_shot_button.configure(highlightbackground="white")
            parent_shot_button.configure(highlightbackground="orange")
            selected_shot_button  = parent_shot_button

            # Find grandpa button (scene) and highlight
            grandparent_scene_button = map_shot_to_scene[parent_shot_button]
            if selected_scene_button:
               selected_scene_button.configure(highlightbackground="white")
            grandparent_scene_button.configure(highlightbackground="yellow")
            selected_scene_button = grandparent_scene_button


         print(f"Frame num {frame_num}")
         self.pause()
         self.is_jump = True
         self.current_frame = frame_num
      return jump_command 


# Start of the code
def main():

   #IndexCreation = CreateIndex('ReadyPlayerOne_InputVideo.mp4')
   # Scene Changes & Shot Changes
   #scene_frames, shot_frames = IndexCreation.scene_frames, IndexCreation.shot_frames
   #scene_frames = [1,2,3,4,5,6,7,8,9,10, 11, 12, 13,14,15,16,17,18,19, 20, 21,22,23,24, 25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,41, 8000]
   #scene_frames = [1,2,3,4,5,6,7,8,9,10, 11, 12, 13,14]
   '''scene_frames = [1, 4100, 8200]
   shot_frames = [1, 600, 3000, 4100, 5000, 8200]
   subshot_frames = [1, 40, 100, 500, 600, 800, 3000, 3200, 3900, 4100, 5000, 6000, 7800, 8100, 8200]  # Optional'''

   mp4_file = sys.argv[1]
   wav_file = sys.argv[2]

   IndexCreation = CreateIndex(mp4_file)
   #IndexCreation = CreateIndex('Gatsby_InputVideo.mp4')
   # Scene Changes & Shot Changes
   scene_frames, shot_frames, subshot_frames = IndexCreation.scene_frames, IndexCreation.shot_frames, IndexCreation.subshot_frames

   print("scene arr size: " +  str(len(scene_frames)))
   print(scene_frames)
   print()

   print("shot arr size: " + str(len(shot_frames)))
   print(shot_frames)
   print()

   print("SUBshot arr size: " + str(len(subshot_frames)))
   print(subshot_frames)
   print()
   '''scene_frames = [1, 4100]
   shot_frames = [1, 3000, 4100, 5000]
   subshot_frames = [1, 40, 100, 600, 3000, 3200, 3900, 4100, 5000, 5600]  # Optional
   print(len(scene_frames))
   print(len(shot_frames))
   print(len(subshot_frames))'''

   #VideoPlayer(tkinter.Tk(), "Tkinter and OpenCV", 'Gatsby_InputVideo.mp4', 'Gatsby_InputAudio.wav', scene_frames, shot_frames, subshot_frames)
   VideoPlayer(tkinter.Tk(), "Tkinter and OpenCV", mp4_file, wav_file, scene_frames, shot_frames, subshot_frames)

   



if __name__ == "__main__":
   main()