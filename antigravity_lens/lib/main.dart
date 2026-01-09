import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:camera/camera.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:antigravity_lens/services/api_service.dart';
import 'package:antigravity_lens/models/profile.dart';
import 'package:antigravity_lens/widgets/truth_card.dart';

List<CameraDescription> cameras = [];

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    cameras = await availableCameras();
  } catch (e) {
    debugPrint("Camera Error: $e");
  }

  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
  ));

  runApp(const AntigravityApp());
}

class AntigravityApp extends StatelessWidget {
  const AntigravityApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Antigravity Lens',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: Colors.white,
        scaffoldBackgroundColor: Colors.black,
        useMaterial3: true,
        textTheme:
            GoogleFonts.outfitTextTheme(Theme.of(context).textTheme).apply(
          bodyColor: Colors.white,
          displayColor: Colors.white,
        ),
      ),
      home: const LensScreen(),
    );
  }
}

class LensScreen extends StatefulWidget {
  const LensScreen({super.key});

  @override
  State<LensScreen> createState() => _LensScreenState();
}

class _LensScreenState extends State<LensScreen> with TickerProviderStateMixin {
  CameraController? controller;
  bool isScanning = false;
  List<UserProfile> activeProfiles = [];

  @override
  void initState() {
    super.initState();
    _initCamera();
    activeProfiles = UserProfile.getDefaults(); // Default: Activate All
  }

  Future<void> _initCamera() async {
    if (cameras.isEmpty) return;
    controller =
        CameraController(cameras[0], ResolutionPreset.high, enableAudio: false);
    try {
      await controller!.initialize();
      if (!mounted) return;
      setState(() {});
    } catch (e) {
      debugPrint("Camera Init Error: $e");
    }
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }

  Future<void> _captureAndScan() async {
    if (controller == null || !controller!.value.isInitialized || isScanning)
      return;

    setState(() {
      isScanning = true;
    });

    try {
      // 1. Capture
      final XFile image = await controller!.takePicture();

      // 2. Scan (Call Backend)
      final result = await ApiService.scanImage(image.path, activeProfiles);

      // 3. Keep Loading specific time for effect? No, wait for result.
      if (!mounted) return;

      // 4. Show Result
      _showResultDialog(result);
    } catch (e) {
      _showResultDialog("Error: $e");
    } finally {
      if (mounted)
        setState(() {
          isScanning = false;
        });
    }
  }

// ... (imports remain)

  void _showResultDialog(String text) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => TruthCard(
        resultText: text,
        onClose: () => Navigator.pop(context),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (controller == null || !controller!.value.isInitialized) {
      return const Scaffold(
          body: Center(child: CircularProgressIndicator(color: Colors.white)));
    }

    return Scaffold(
      body: Stack(
        fit: StackFit.expand,
        children: [
          // 1. Camera Preview
          CameraPreview(controller!),

          // 2. Scanning Overlay (Animation)
          if (isScanning)
            Container(color: Colors.black54)
                .animate(onPlay: (c) => c.repeat(reverse: true))
                .shimmer(duration: 1500.ms, color: Colors.white24),

          if (isScanning)
            const Center(
                child:
                    Text("ANALYZING...", style: TextStyle(letterSpacing: 3))),

          // 3. UI Controls
          SafeArea(
            child: Column(
              children: [
                // Header
                Padding(
                  padding: const EdgeInsets.all(20),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Icon(Icons.flash_off, color: Colors.white),
                      const Text("ANTIGRAVITY",
                          style: TextStyle(
                              fontWeight: FontWeight.bold, letterSpacing: 2)),
                      GestureDetector(
                        onTap: () {
                          // Toggle Profiles Dialog
                        },
                        child: CircleAvatar(
                          radius: 16,
                          backgroundColor: Colors.white24,
                          child: Text(activeProfiles.length.toString(),
                              style: const TextStyle(color: Colors.white)),
                        ),
                      ),
                    ],
                  ),
                ),

                const Spacer(),

                // Scanner Box
                Center(
                    child: Container(
                  width: 280,
                  height: 280,
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.white.withOpacity(0.5)),
                    borderRadius: BorderRadius.circular(24),
                  ),
                ).animate(onPlay: (c) => c.repeat(reverse: true))),

                const Spacer(),

                // Capture Button
                GestureDetector(
                  onTap: _captureAndScan,
                  child: Container(
                    width: 80,
                    height: 80,
                    margin: const EdgeInsets.only(bottom: 40),
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      border: Border.all(color: Colors.white, width: 4),
                    ),
                    child: Center(
                      child: Container(
                        width: 70,
                        height: 70,
                        decoration: BoxDecoration(
                          color: isScanning ? Colors.white38 : Colors.white,
                          shape: BoxShape.circle,
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
