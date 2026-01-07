import moviepy.video.fx
print("dir(moviepy.video.fx):", dir(moviepy.video.fx))

try:
    from moviepy.video.fx import fadein
    print("SUCCESS: from moviepy.video.fx import fadein")
except ImportError:
    print("FAIL: from moviepy.video.fx import fadein")

try:
    from moviepy.video.fx.fadein import fadein
    print("SUCCESS: from moviepy.video.fx.fadein import fadein")
except ImportError:
    print("FAIL: from moviepy.video.fx.fadein import fadein")
