import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:camera/camera.dart';
import 'package:antigravity_lens/screens/camera_screen.dart';

List<CameraDescription> _cameras = [];

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 1. Initialize Cameras (DISABLED FOR DEBUGGING)
  try {
    // _cameras = await availableCameras();
    debugPrint("Skipping Camera Init for Debugging");
  } catch (e) {
    debugPrint("Camera Fetch Error: $e");
  }

  SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark, // Dark icons for light background
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
        brightness: Brightness.light, // Morandi is Light/Soft
        primaryColor: const Color(0xFF9CAF88), // Sage Green
        scaffoldBackgroundColor: const Color(0xFFFDFBF7), // Cream
        useMaterial3: true,
        textTheme:
            GoogleFonts.outfitTextTheme(Theme.of(context).textTheme).apply(
          bodyColor: const Color(0xFF4A4A4A), // Charcoal
          displayColor: const Color(0xFF4A4A4A),
        ),
      ),
      // Directly to Camera Screen for "Easy to Use" experience
      home: _cameras.isEmpty
          ? const Scaffold(body: Center(child: Text("No Camera Found")))
          : CameraScreen(cameras: _cameras),
    );
  }
}
