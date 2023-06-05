# Video Index Creation with an Interactive Player
 
 For the full, detailed project description, please take a look at Project_Description.pdf. To run the program, enter the following command into terminal: "python VideoPlayer.py [insert mp4 file] [insert wav file]", e.g. "python VideoPlayer.py ReadyPlayerOne_InputVideo.mp4 ReadyPlayerOne_InputAudio.wav".


  **Synopsis**: 
In this project, we develop a solution to:
1. Arrive at a logical index or table of contents in an automated manner given a video with audio as input.
2. Once the index or table of contents is extracted, we show it in an interactive player setup where you can jump to any index to browse the video/audio and change it interactively allowing interactive exploration.

 In this repository, the two main files are VideoPlayer.py and IndexCreation.py. The main function is in VideoPlayer.py: it initiates and creates the interactive video player that includes buttons to play, pause, and stop (rewind current scene/shot/subshot), and buttons to jump to different scenes/shots/subshots. IndexCreation.py is where the given video is indexed. It creates a list of scenes/shots/subshots; these are the video frames of where the video should be separated and deemed as a different scene/shot/subshot. Moreover, there are three provided test files that could be used to test the program on: ReadyPlayerOne_InputVideo.mp4 + ReadyPlayerOne_InputAudio.wav, LongDark_InputVideo.mp4 + LongDark_InputAudio.wav, Gatsby_InputVideo.mp4 + Gatsby_InputAudio.wav.


**Notes**:
- The video width and height of the video will be fixed (480x270).
- The sampling rate of the audio will be fixed.
- The video FPS is generalized, typically tested on 30 fps or 24 fps.
- The required length of the video will vary - **IMPORTANT**: the index creation is tailored and optimized for video clips that are at least 2 minutes in length.