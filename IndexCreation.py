import cv2 as cv
import numpy as np

class CreateIndex:
    
   def __init__(self, video_file):
      self.scene_frames, self.shot_frames, self.subshot_frames = self.get_frame_changes(video_file)


   def get_frame_changes(self, vid):

      cap = cv.VideoCapture(vid)
      if not cap.isOpened():
         print("Error opening video file")

      # return values
      scenes = []
      shots = []
      subshots = []

      # Use the 0-th and 1-st channels
      channels = [0, 1, 2]

      ## [Using 50 bins for hue and 60 for saturation]
      h_bins = 50
      s_bins = 50
      v_bins = 50
      histSize = [h_bins, s_bins, v_bins]

      # hue varies from 0 to 179, saturation from 0 to 255
      h_ranges = [0, 180]
      s_ranges = [0, 256]
      v_ranges = [0, 256]
      ranges = h_ranges + s_ranges + v_ranges# concat lists

      frame_num = 0

      # chi Sqr for scene change detection
      chi_sqr_coeff = []
      frame_to_chi_sqr = {}

      # bhattacharya for shot change detection
      bhattacharyya_coeff = []
      frame_to_butter_chia = {}

      count = 0
      prev_frame = 0
      ret = False

      if cap.isOpened():
         # Read the current frame
         ret, prev_frame = cap.read()

      while cap.isOpened():

         ret, cur_frame = cap.read()

         # If the frame was read successfully, process it
         if ret:
            # Perform any image processing or analysis on the frame here
            frame_num += 1

            # Convert it to HSV
            frame_prev_hsv = cv.cvtColor(prev_frame, cv.COLOR_BGR2HSV)
            frame_cur_hsv = cv.cvtColor(cur_frame, cv.COLOR_BGR2HSV)

            hist_prev = cv.calcHist([frame_prev_hsv], channels, None, histSize, ranges, accumulate=False)
            cv.normalize(hist_prev, hist_prev, alpha=0, beta=1, norm_type=cv.NORM_MINMAX)

            hist_cur = cv.calcHist([frame_cur_hsv], channels, None, histSize, ranges, accumulate=False)
            cv.normalize(hist_cur, hist_cur, alpha=0, beta=1, norm_type=cv.NORM_MINMAX)

            chi_sqr_metric_val = cv.compareHist(hist_prev, hist_cur, cv.HISTCMP_CHISQR) 
            bhattacharyya_metric_val = cv.compareHist(hist_prev, hist_cur, cv.HISTCMP_BHATTACHARYYA)

            chi_sqr_coeff.append(chi_sqr_metric_val)
            bhattacharyya_coeff.append(bhattacharyya_metric_val)

            frame_to_chi_sqr[frame_num] = chi_sqr_metric_val
            frame_to_butter_chia[frame_num] = bhattacharyya_metric_val


         else:
            break

         count += 1
         prev_frame = cur_frame

      cap.release()
      cv.destroyAllWindows()

      # FOR NOW: Our final thresholds are as follows: DO NOT DELETE BELOW CODE
      '''chi_SCENE_thresh = np.mean(chi_sqr_coeff) + 8*np.std(chi_sqr_coeff)
      bhat_SCENE_thresh = np.mean(bhattacharyya_coeff) + 8*np.std(bhattacharyya_coeff)

      chi_SHOT_thresh = np.mean(chi_sqr_coeff) + 3*np.std(chi_sqr_coeff)
      bhat_SHOT_thresh = np.mean(bhattacharyya_coeff) + 3*np.std(bhattacharyya_coeff)

      chi_SUBshot_thresh = np.mean(chi_sqr_coeff) + 2*np.std(chi_sqr_coeff)
      bhat_SUBshot_thresh = np.mean(bhattacharyya_coeff) + 2*np.std(bhattacharyya_coeff)'''

      chi_SCENE_thresh = np.mean(chi_sqr_coeff) + 3*np.std(chi_sqr_coeff)
      bhat_SCENE_thresh = np.mean(bhattacharyya_coeff) + 3*np.std(bhattacharyya_coeff)

      chi_SHOT_thresh = np.mean(chi_sqr_coeff) + 2*np.std(chi_sqr_coeff)
      bhat_SHOT_thresh = np.mean(bhattacharyya_coeff) + 2*np.std(bhattacharyya_coeff)

      chi_SUBshot_thresh = np.mean(chi_sqr_coeff) + np.std(chi_sqr_coeff)
      bhat_SUBshot_thresh = np.mean(bhattacharyya_coeff) + np.std(bhattacharyya_coeff)

      scenes.append(1)
      shots.append(1)
      subshots.append(1)

      for chi, bhat in zip(frame_to_chi_sqr, frame_to_butter_chia):
         # Add to scenes
         if frame_to_chi_sqr[chi]>chi_SCENE_thresh and frame_to_butter_chia[bhat]>bhat_SCENE_thresh:
            scenes.append(chi+1)

         # Add to shots
         if frame_to_chi_sqr[chi]>chi_SHOT_thresh and frame_to_butter_chia[bhat]>bhat_SHOT_thresh:
            shots.append(chi+1)

         # Add to subshots
         if frame_to_chi_sqr[chi]>chi_SUBshot_thresh and frame_to_butter_chia[bhat]>bhat_SUBshot_thresh:
            subshots.append(chi+1)


      # Clean up the arrays: take out frames that are really close to each other
      '''
      - For subshots, combine frames that are within 1, 2, or 3 seconds of each other (30, 60, 90 frames)
      - For shots, combine frames that are within 4, 5, 6 seconds of each other (120, 150, 180 frames)
      - For scenes, combine frames that are withing 7+ seconds of each other (210+ frames)

      Constraints:
      - subshots -- do NOT take out frames that exist in the shots array
      - shots -- do NOT take out frames that exist in the scenes array
      '''
   
      # Filter the scenes
      new_scenes = []
      prev_scene = -float('inf')
      for i, scen in enumerate(scenes):
         if abs(scen-prev_scene) > 300: # was 120
            new_scenes.append(scen)
            prev_scene = scen

      scenes = new_scenes

      new_shots = []
      prev_shot = -float('inf')
      for i, sh in enumerate(shots):
         # Case before reaching the last element
         if i < len(shots)-1:
            if sh in scenes:
               new_shots.append(sh)
               prev_shot = sh

            # Compare with prev shot and next
            elif abs(sh-prev_shot) > 150 and abs(sh-shots[i+1]) > 150: # try 6 or 7 seconds, was 3
               new_shots.append(sh)
               prev_shot = sh

         # We are at last element
         else:
            if sh in scenes:
               new_shots.append(sh)
               prev_shot = sh
            elif abs(sh-prev_shot) > 150: # try 6 or 7 seconds, was 3
               new_shots.append(sh)
               prev_shot = sh

      shots = new_shots

      new_subshots = []
      prev_SUBshot = -float('inf')
      for i, sub in enumerate(subshots):
         # Case before reaching the last element
         if i < len(subshots)-1:
            if sub in shots:
               new_subshots.append(sub)
               prev_SUBshot = sub
            
            # Compare with prev subshot and next
            elif abs(sub-prev_SUBshot) > 60 and abs(sub-subshots[i+1]) > 60: # try 3 seconds, was 2
               new_subshots.append(sub)
               prev_SUBshot = sub

         # We are at the last element
         else:
            if sub in shots:
               new_subshots.append(sub)
               prev_SUBshot = sub
            elif abs(sub-prev_SUBshot) > 60: # try 3 seconds, was 2
               new_subshots.append(sub)
               prev_SUBshot = sub
      
      subshots = new_subshots

      #############################
      '''scene_threshold = np.mean(chi_sqr_coeff) + 12*np.std(chi_sqr_coeff)
      scenes.append(1)
      for item in frame_to_chi_sqr:
         if frame_to_chi_sqr[item] > scene_threshold:
            scenes.append(item+1)

      shot_threshold = np.mean(bhattacharyya_coeff) + 8*np.std(bhattacharyya_coeff)
      shots.append(1)
      for item in frame_to_butter_chia:
         if frame_to_butter_chia[item] > shot_threshold:
            shots.append(item+1)'''

      # Our video player algorithm is such that it will form the buttons based on the following fact:
      # It must be that all the frames in the scene array is in the shot array
      # Similarly, it must be that all the frames in the shot array is in the subshots array
      # i.e. scenes is a subset of shots is a subset of subshots
      # print(len(self.intersection(scenes, shots)))
      # if len(self.intersection(scenes, shots)) != len(scenes):

      return scenes, shots, subshots
   

   #def intersection(self, list_1, list_2):
      #return list(set(list_1) & set(list_2))
   


'''
- process the array such that 2 frames that are close to each other are deemed as 1 frame
'''

'''
- consider audio
- use statistics of each video - mean, std, etc.
- log transform the data - what data do you wanna pull
- use frame difference
   - look into the motion in each frame
- Edge detection
- use average of 2 different methods and find the average/intersection (range)
   - compute multiple methods and compare all the arrays they produced -- come up with a final array
- optical flow
'''