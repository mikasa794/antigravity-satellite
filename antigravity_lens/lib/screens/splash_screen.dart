import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
// import 'package:audioplayers/audioplayers.dart'; // Import Audio
// import 'package:audioplayers/audioplayers.dart'; // Import Audio

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  bool showFace = false;
  // late AudioPlayer _sfxPlayer;
  // late AudioPlayer _bgmPlayer;

  @override
  void initState() {
    super.initState();
    // _sfxPlayer = AudioPlayer();
    // _bgmPlayer = AudioPlayer();
    _startSequence();
  }

  @override
  void dispose() {
    // _sfxPlayer.dispose();
    // _bgmPlayer.dispose();
    super.dispose();
  }

  Future<void> _startSequence() async {
    // 0. Start Sound (Boing / Jingle)
    /*
    _sfxPlayer.play(AssetSource('splash_boing.wav')).then((_) {}, onError: (e) {
      print("Audio Error: $e");
    });
    */

    // 1. Bounce Loop (Ball)
    await Future.delayed(2200.ms);

    if (!mounted) return;

    // Play Pop Sound
    /*
    try {
      _sfxPlayer.stop().then((_) {
         _sfxPlayer.play(AssetSource('splash_pop.wav'));
      });
    } catch (e) {
      print("Audio Error: $e");
    }

    // Play Magic BGM (Layered)
    _bgmPlayer.play(AssetSource('splash_magic.wav'), volume: 0.8).catchError((e) {
      print("Audio Error: $e");
    });
    */

    setState(() {
      showFace = true; // Swap to Face
    });

    // 2. Pose (Face)
    await Future.delayed(2500.ms);

    if (!mounted) return;
    // 3. Go to Home (Camera)
    // For now, we rely on Main to route. This Splash is standalone.
    // verification: just pop or do nothing if this is just a demo.
    // But to be proper:
    // Navigator.of(context).pushReplacement(... CameraScreen ...);
    // Since we didn't pass cameras here, let's just leave a TODO or fix main to use Splash.

    // TEMPORARY FIX: Just print "Splash Done" until we wire up global state or provider.
    debugPrint("Splash Sequence Complete");
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // LAYER 1: Static Background
          Positioned.fill(
            child: Image.asset(
              'assets/splash_bg.png',
              fit: BoxFit.cover,
            ),
          ),

          // LAYER 2: Bouncing Character
          Center(
            child: showFace
                // FINAL STATE: FACE
                ? Container(
                    // Optional: Add shadow if missing from asset
                    /* decoration: BoxDecoration(
                      boxShadow: [
                         BoxShadow(color: Colors.black12, blurRadius: 20, offset: Offset(0, 10))
                      ]
                    ), */
                    child: Image.asset(
                      'assets/splash_char_final.png',
                      width: 250,
                      height: 250,
                    )
                        .animate()
                        .scale(
                            duration: 400.ms,
                            curve: Curves.elasticOut,
                            begin: const Offset(0.8, 0.8)) // Pop
                        .shake(
                            duration: 400.ms,
                            hz: 3,
                            curve: Curves.easeInOut), // Cute shake
                  )

                // INTRO STATE: BALL
                : Image.asset(
                    'assets/splash_char_intro.png',
                    width: 250,
                    height: 250,
                  )
                    .animate(
                        onPlay: (controller) =>
                            controller.repeat(reverse: true))
                    .moveY(
                        begin: 0,
                        end: -40,
                        duration: 600.ms,
                        curve: Curves.easeInOut) // BOING
                    .scaleXY(
                        begin: 1.0,
                        end: 1.05,
                        duration: 600.ms,
                        curve: Curves.easeInOut) // Squash
                    .effect(duration: 600.ms),
          ),
        ],
      ),
    );
  }
}
