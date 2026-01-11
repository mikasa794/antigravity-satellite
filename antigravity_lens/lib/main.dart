import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:camera/camera.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:antigravity_lens/services/api_service.dart';
import 'package:antigravity_lens/models/profile.dart';
import 'package:antigravity_lens/widgets/truth_card.dart';
import 'package:antigravity_lens/services/history_service.dart';
import 'package:antigravity_lens/models/scan_record.dart';
import 'package:antigravity_lens/screens/history_screen.dart';
import 'package:antigravity_lens/screens/splash_screen.dart'; // Add Splash Import

List<CameraDescription> cameras = [];

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Fire-and-forget Camera Init (Don't block UI start)
  availableCameras().then((value) {
    cameras = value;
  }).catchError((e) {
    debugPrint("Camera Error: $e");
  });

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
      home: const SplashScreen(),
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
  List<UserProfile> allProfiles = [];

  @override
  void initState() {
    super.initState();
    _initCamera();
    allProfiles = UserProfile.getDefaults();
    activeProfiles = List.from(allProfiles); // Default: Activate All
  }

  Future<void> _initCamera() async {
    if (cameras.isEmpty) return;
    controller = CameraController(cameras[0], ResolutionPreset.medium,
        enableAudio: false);
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
      final result = await ApiService.scanImage(image, activeProfiles);

      // 3. Save to History (Memory Lane)
      final now = DateTime.now();
      await HistoryService.saveRecord(ScanRecord(
        id: now.millisecondsSinceEpoch.toString(),
        date:
            "${now.year}-${now.month}-${now.day} ${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}",
        result: result,
      ));

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
                      // History Button
                      GestureDetector(
                        onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (c) => const HistoryScreen())),
                        child: CircleAvatar(
                          radius: 20,
                          backgroundColor: Colors.white10,
                          child: const Icon(Icons.history,
                              color: Colors.white, size: 20),
                        ),
                      ),
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

                // Profile Selector (Family Shield)
                SizedBox(
                  height: 60,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    itemCount: allProfiles.length,
                    itemBuilder: (context, index) {
                      final profile = allProfiles[index];
                      final isActive = activeProfiles.contains(profile);
                      return GestureDetector(
                        onTap: () {
                          setState(() {
                            if (isActive) {
                              activeProfiles.remove(profile);
                            } else {
                              activeProfiles.add(profile);
                            }
                          });
                        },
                        child: AnimatedContainer(
                          duration: 200.ms,
                          margin: const EdgeInsets.only(right: 12),
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 8),
                          decoration: BoxDecoration(
                            color: isActive
                                ? Colors.white
                                : Colors.white.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(30),
                            border: Border.all(
                                color: isActive
                                    ? Colors.transparent
                                    : Colors.white30),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                profile.isPet ? Icons.pets : Icons.person,
                                size: 16,
                                color: isActive ? Colors.black : Colors.white,
                              ),
                              const SizedBox(width: 8),
                              Text(
                                profile.name.split(' ')[0], // First name only
                                style: TextStyle(
                                  color:
                                      isActive ? Colors.black : Colors.white70,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),

                const SizedBox(height: 20),

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
