
# TikTok automation import
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# rendering import
from pathlib import Path
import socket
from snake import Snake
from moviepy.editor import *


# other params
chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe"
channel_url = 'https://www.tiktok.com/@souls46'
local_wait = 1
wait_time = 600  # in seconds

# render server params
render_server_info = ('127.0.0.1', 5124)

# ------------------------------------------------------------- TikTok automation functions

# -- pre-init
# open a chrome on given port {use cmd}
# chrome.exe --remote-debugging-port=5125

# open renderer
# java -cp "snake_render\snake_render.jar;snake_render\*;." snake_render


# get current date time
def get_current_time_str():
    datetime_now = datetime.now()
    return datetime_now.strftime("%H:%M:%S")

# return a string such 100k to float
def value_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace('B', '')) * 1000000000
    if type(x) == str:
        try:
            return float(x)
        except ValueError:
            return 0.0
    return 0.0


# Get the latest video of given profile
def get_latest_vid_info(url):

    # synchronised wait time
    global local_wait

    while True:
        try:
            driver.get(url)
            time.sleep(local_wait)
            latest_vid = driver.find_element_by_xpath("//div[contains(@class, 'DivItemContainer')]")
            latest_vid.click()

            time.sleep(local_wait)
            driver.get(driver.current_url)

            likes = value_to_float(
                driver.find_element_by_xpath("//strong[@data-e2e='like-count']").get_property('innerText'))
            comments = value_to_float(
                driver.find_element_by_xpath("//strong[@data-e2e='comment-count']").get_property('innerText'))
            shares = value_to_float(
                driver.find_element_by_xpath("//strong[@data-e2e='share-count']").get_property('innerText'))

            stats = [likes, comments, shares]
            print(get_current_time_str() + ': retrieved stats', stats)

            # go back to google
            driver.get('https://www.google.com')
            return stats

        except:
            local_wait *= 2
            print('Something went wrong, trying again')

            if local_wait > 100:
                return False


# The upload sequence
def upload_video(location, wait, cur_caption):

    # synchronised wait time
    global local_wait

    while True:
        try:
            driver.get('https://www.tiktok.com/upload?lang=en')
            time.sleep(local_wait)

            # switches to upload frame
            driver.switch_to.frame(0)

            upload_inp = driver.find_element_by_xpath("//input[@type='file']")
            upload_inp.send_keys(location)

            editor = driver.find_element_by_xpath("//div[contains(@class, 'public-DraftEditor-content')]")
            editor.click()
            editor.clear()

            time.sleep(local_wait)
            editor.send_keys(cur_caption)

            time.sleep(local_wait * 2)
            post = driver.find_element_by_xpath("//button[@class='tiktok-btn-pc tiktok-btn-pc-large tiktok-btn-pc-primary']")
            post.click()

            # switches back to main content
            driver.switch_to.default_content()

            print(get_current_time_str() + ': Video uploaded')

            # go back to google
            driver.get('https://www.google.com')
            return True

        except:
            local_wait *= 2
            print('Something went wrong, trying again')

            if wait > 200:
                return False


options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:5125")
driver = webdriver.Chrome(chrome_path, options=options)


# ------------------------------------------------------------- Render functions

# path variables
path = str(Path().resolve().parent.absolute())
images_render_path = path + r'\rendered_images'
renderer_path = path + r'\snake_render'


# generate images function
def generate_images():

    # get server information
    global render_server_info

    # with socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as render_server:

        # connect to render server
        render_server.connect((render_server_info[0], render_server_info[1]))

        # send record command
        render_server.send(b'record')

        # wait for complete message -> decode to ascii
        payload = render_server.recv(1024).decode('ascii')

    # if complete
    if payload == 'complete':
        return True
    return False


# get rendered images
def rendered_images():
    img_list = os.listdir(images_render_path)
    for i in range(len(img_list)):
        img_list[i] = images_render_path + "\\" + img_list[i]
    return img_list


# delete the rendered images
def delete_images():
    for img in rendered_images():
        os.remove(img)


# create video
def create_video(video_name):
    clips = [ImageClip(img).set_duration(1) for img in rendered_images()]
    video = concatenate_videoclips(clips, method='compose')
    video.write_videofile(video_name, fps=1, remove_temp=True, codec='libx264', audio_codec='aac')


# caption creation
def get_caption():
    return ' SnakeBot! Check the latest post for current state of snake!'


# get the movement from video information
def get_movement_from_info(info):
    movement = 0
    for i in range(len(info)):
        if info[i] > info[movement]:
            movement = i
    print('moving', movement)
    return movement


# ------------------------------------------------------------- Game Loop

# sequence of operations
# 1. render video
#  1.1. upload video
# 2. wait {minutes} -> get likes, comments and share ratios
#  2.1. use the info to move the snake
#  2.2. save snake state to disk
# loop

# some functions
# console render
# snake_game.console_render()

# delete previous image renders -> not needed at the moment
# delete_images()

# Snake Game -> Initialise
# World X, World Y, State path
snake_game = Snake(10, 10, path + r'\state.txt')

# Start Game -> takes boolean to specify whether it will
# True: load from state or
# False: start a new game
snake_game.start_game(True)

# gets info first when launching program -> rather than uploading the current state
ignore_upload = True


# Main Game Loop
while True:

    # fetch data first
    if not ignore_upload:

        # save state
        snake_game.save_state()

        # generate images, based on state
        if generate_images() is False:
            input(get_current_time_str() + ': Waiting... Generate images failed')

        # create video based on images
        create_video(path + r'\video.mp4')

        # if can't retrieve info after 200 seconds
        if upload_video(path + r'\video.mp4', 1, get_caption()) is False:
            input(get_current_time_str() + ': Waiting... Upload failed')

    # container for video interaction
    vid_info = [0, 0, 0]

    # if nobody has interacted, then keep waiting
    while True:

        # don't wait if ignore upload is set to true
        if not ignore_upload:

            # check if there was an interaction -> if there was, stop waiting
            if max(vid_info) > 0:
                break

            # wait for reactions -> default should 10, debugging is 1 (in minutes) | param at the top of file
            time.sleep(wait_time)

        # get the latest video information [likes, comments, shares]
        vid_info = get_latest_vid_info(channel_url)

        # if can't retrieve info after 200 seconds
        if vid_info is False:
            input(get_current_time_str() + ': Waiting... Retrieving Video Info failed')

        # after info has been fetched
        ignore_upload = False

    # get the movement code from video info
    move = get_movement_from_info(vid_info)

    # do the movement
    if move == 1:
        snake_game.left()  # comment
    elif move == 2:
        snake_game.right()  # share

    # do a forward move
    snake_game.move()

