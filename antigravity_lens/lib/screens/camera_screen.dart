import 'dart:ui';
import 'package:antigravity_lens/screens/add_profile_screen.dart';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/profile.dart';
import '../services/api_service.dart';
import '../widgets/truth_card.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key});

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _controller;
  bool _isInit = false;
  bool _isScanning = false;

  // Morandi Light Palette
  final Color _bgLight = const Color(0xFFF2F2F7); // iOS Light Grey
  final Color _glassWhite = Colors.white.withOpacity(0.85); // Frosted White
  final Color _charcoal = const Color(0xFF333333); // Soft Dark Text
  final Color _sageGreen = const Color(0xFF9CAF88);
  final Color _cream = const Color(0xFFFDFBF7);

  List<UserProfile> _profiles = [];
  late UserProfile _selectedProfile;

  @override
  void initState() {
    super.initState();
    // Camera is NOT initialized by default.
    _loadProfiles();
  }

  void _loadProfiles() {
    _profiles = UserProfile.getDefaults();
    _selectedProfile = _profiles.first; // Default to Shin-chan (Me)
  }

  Future<void> _initCamera() async {
    try {
      final cameras = await availableCameras();
      if (cameras.isEmpty) {
        throw Exception("No cameras found");
      }

      // 1. Find Back Camera
      CameraDescription? backCamera;
      for (var cam in cameras) {
        if (cam.lensDirection == CameraLensDirection.back) {
          backCamera = cam;
          break;
        }
      }
      final targetCamera = backCamera ?? cameras[0];

      // 2. Initialize (Medium Res for Web Stability)
      _controller = CameraController(targetCamera, ResolutionPreset.medium,
          enableAudio: false);

      await _controller!.initialize();
      if (!mounted) return;
      setState(() => _isInit = true);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text("Error: $e")));
      }
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  void _takePicture() async {
    if (_isScanning || !_isInit || _controller == null) return;
    setState(() => _isScanning = true);

    try {
      final image = await _controller!.takePicture();
      // Simulate Scan Delay for "AI Thinking" vibe
      await Future.delayed(1500.ms);

      // Call Satellite API
      final result =
          await ApiService.scanImage(image, _profiles, _selectedProfile);

      // Show Result (TruthCard)
      if (mounted) {
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          backgroundColor: Colors.transparent,
          builder: (context) => DraggableScrollableSheet(
            initialChildSize: 0.6,
            minChildSize: 0.4,
            maxChildSize: 0.9,
            builder: (_, scroll) => Container(
              decoration: BoxDecoration(
                color: _cream,
                borderRadius:
                    const BorderRadius.vertical(top: Radius.circular(30)),
              ),
              child: TruthCard(
                resultText: result,
                onClose: () => Navigator.pop(context),
              ),
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text("Scan Failed: $e")));
      }
    } finally {
      if (mounted) setState(() => _isScanning = false);
    }
  }

  void _addInfo() async {
    final newProfile = await Navigator.push(context,
        MaterialPageRoute(builder: (context) => const AddProfileScreen()));

    if (newProfile != null && newProfile is UserProfile) {
      setState(() {
        _profiles.add(newProfile);
        _selectedProfile = newProfile;
      });
    }
  }

  // Helper for Profile Icons/Colors (Morandi x Crayon Shin-chan)
  Color _getProfileColor(UserProfile p) {
    if (p.id.contains('hiroshi'))
      return const Color(0xFF7E9AA8); // Dusty Blue (Dad)
    if (p.id.contains('misae'))
      return const Color(0xFFD4A5A5); // Dusty Pink (Mom)
    if (p.id.contains('shinchan'))
      return const Color(0xFFD98E73); // Terracotta (Red Shirt)
    if (p.id.contains('himawari'))
      return const Color(0xFFEACD76); // Straw Yellow (Hima)
    if (p.id.contains('shiro'))
      return const Color(0xFFCFCFCF); // Cloud Grey (Shiro)
    if (p.id.contains('antigravity'))
      return const Color(0xFFB5A1C0); // Lavender (You)
    return _sageGreen; // Default
  }

  IconData _getProfileIcon(UserProfile p) {
    if (p.isPet) return Icons.pets; // Shiro
    if (p.id.contains('antigravity')) return Icons.auto_awesome;
    if (p.id.contains('hiroshi')) return Icons.business_center; // Office Worker
    if (p.id.contains('misae')) return Icons.shopping_bag; // Housewife/Shopping
    if (p.id.contains('himawari')) return Icons.child_friendly; // Baby
    return Icons.face; // Shin-chan
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bgLight,
      body: Stack(
        children: [
          // 1. Camera Feed / Placeholder
          if (_isInit && _controller != null)
            SizedBox.expand(
              child: FittedBox(
                fit: BoxFit.cover,
                child: SizedBox(
                  width: _controller!.value.previewSize!.height,
                  height: _controller!.value.previewSize!.width,
                  child: CameraPreview(_controller!),
                ),
              ),
            )
          else
            Center(
                child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                  Icon(Icons.camera_alt_outlined,
                      size: 80, color: _sageGreen.withOpacity(0.3)),
                  const SizedBox(height: 20),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 40),
                    child: Text(
                        "Tap 'Open Lens' to scan food, beauty & daily items.",
                        textAlign: TextAlign.center,
                        style: GoogleFonts.outfit(
                            color: _charcoal.withOpacity(0.6), fontSize: 16)),
                  )
                ])),

          // 2. Top Bar (Morandi Pill - Light Mode)
          SafeArea(
            child: Align(
              alignment: Alignment.topCenter,
              child: Padding(
                padding: const EdgeInsets.only(top: 20),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(30),
                  child: BackdropFilter(
                    filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 20, vertical: 10),
                      color: _glassWhite, // Light Frosted Glass
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          // Dynamic Icon based on Selection
                          Icon(_getProfileIcon(_selectedProfile),
                              color: _getProfileColor(_selectedProfile),
                              size: 18),
                          const SizedBox(width: 8),
                          Text(
                            "ANTIGRAVITY LENS",
                            style: GoogleFonts.outfit(
                                color: _charcoal, // Dark Text
                                fontWeight: FontWeight.w600,
                                letterSpacing: 1.2),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),

          // 3. Bottom Control Board (Light Gradient)
          Align(
            alignment: Alignment.bottomCenter,
            child: Container(
              height: 240,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.bottomCenter,
                  end: Alignment.topCenter,
                  colors: [
                    Colors.white.withOpacity(0.95), // White Base
                    Colors.white.withOpacity(0.0), // Fade to transparent
                  ],
                  stops: const [0.6, 1.0],
                ),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  // Profile Selector
                  SizedBox(
                    height: 80, // Taller for avatars
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      padding: const EdgeInsets.symmetric(horizontal: 20),
                      itemCount: _profiles.length + 1,
                      itemBuilder: (context, index) {
                        if (index == _profiles.length) {
                          // Add Button
                          return Padding(
                            padding: const EdgeInsets.only(
                                right: 15, top: 10), // Align with avatars
                            child: GestureDetector(
                              onTap: _addInfo,
                              child: CircleAvatar(
                                radius: 28,
                                backgroundColor: Colors.grey[200],
                                child: Icon(Icons.add, color: _charcoal),
                              ),
                            ),
                          );
                        }

                        final profile = _profiles[index];
                        final isSelected = profile == _selectedProfile;
                        final pColor = _getProfileColor(profile);
                        String? assetPath = profile.avatarPath;
                        if (assetPath == null) {
                          if (profile.id.contains('shinchan'))
                            assetPath = 'assets/avatars/shinchan_icon.png';
                          else if (profile.id.contains('hiroshi'))
                            assetPath = 'assets/avatars/hiroshi_icon.png';
                          else if (profile.id.contains('misae'))
                            assetPath = 'assets/avatars/misae_icon.png';
                          else if (profile.id.contains('himawari'))
                            assetPath = 'assets/avatars/himawari_icon.png';
                          else if (profile.id.contains('shiro'))
                            assetPath = 'assets/avatars/shiro_icon.png';
                          else if (profile.id.contains('grandpa'))
                            assetPath = 'assets/avatars/grandpa_icon.png';
                        }
                        IconData fallbackIcon = _getProfileIcon(profile);
                        Widget animatedAvatar = AnimatedContainer(
                          duration: 300.ms,
                          margin: const EdgeInsets.only(right: 16),
                          padding: const EdgeInsets.all(3),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                                color: isSelected ? pColor : Colors.transparent,
                                width: 3),
                            boxShadow: isSelected
                                ? [
                                    BoxShadow(
                                        color: pColor.withOpacity(0.3),
                                        blurRadius: 10,
                                        spreadRadius: 2)
                                  ]
                                : null,
                          ),
                          child: CircleAvatar(
                            radius: 28,
                            backgroundColor: Colors.white,
                            child: ClipOval(
                              child: assetPath != null
                                  ? Image.asset(
                                      assetPath,
                                      width: 56,
                                      height: 56,
                                      fit: BoxFit.cover,
                                      errorBuilder:
                                          (context, error, stackTrace) {
                                        return Icon(fallbackIcon,
                                            color: isSelected
                                                ? pColor
                                                : Colors.grey[400],
                                            size: 28);
                                      },
                                    )
                                  : Icon(fallbackIcon,
                                      color: isSelected
                                          ? pColor
                                          : Colors.grey[400],
                                      size: 28),
                            ),
                          ),
                        );
                        bool shouldFloat =
                            profile.isPet || profile.id.contains('antigravity');
                        if (shouldFloat) {
                          return GestureDetector(
                            onTap: () =>
                                setState(() => _selectedProfile = profile),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                animatedAvatar
                                    .animate(
                                        onPlay: (c) => c.repeat(reverse: true))
                                    .moveY(
                                        begin: 0,
                                        end: -6,
                                        duration: 2.seconds,
                                        curve: Curves.easeInOut),
                              ],
                            ),
                          );
                        } else {
                          return GestureDetector(
                            onTap: () =>
                                setState(() => _selectedProfile = profile),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                animatedAvatar
                                    .animate(
                                        onPlay: (c) => c.repeat(reverse: true))
                                    .scaleXY(
                                        begin: 1.0,
                                        end: 1.05,
                                        duration: 3.seconds,
                                        curve: Curves.easeInOut),
                              ],
                            ),
                          );
                        }
                      },
                    ),
                  ),

                  // Selected Name Indicator
                  Padding(
                    padding: const EdgeInsets.only(top: 8, bottom: 30),
                    child: Text(
                      _selectedProfile.name.toUpperCase(),
                      style: GoogleFonts.outfit(
                          color: _charcoal.withOpacity(0.9), // Dark Text
                          fontSize: 14,
                          letterSpacing: 2,
                          fontWeight: FontWeight.w600),
                    ),
                  )
                      .animate(key: ValueKey(_selectedProfile))
                      .fade()
                      .slideY(begin: 0.2, end: 0),

                  const SizedBox(height: 10),

                  // Shutter Button OR Start Button
                  if (_isInit && _controller != null)
                    GestureDetector(
                      onTap: _takePicture,
                      child: Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: Colors.white,
                            border: Border.all(
                                color: _sageGreen.withOpacity(0.8), width: 5),
                            boxShadow: [
                              BoxShadow(
                                  color: Colors.grey.withOpacity(0.2),
                                  blurRadius: 10,
                                  spreadRadius: 2)
                            ]),
                        child: _isScanning
                            ? Padding(
                                padding: const EdgeInsets.all(20),
                                child: CircularProgressIndicator(
                                    color: _sageGreen))
                            : Center(
                                child: Container(
                                    width: 60,
                                    height: 60,
                                    decoration: BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: _sageGreen))),
                      ),
                    ).animate(target: _isScanning ? 1 : 0).scale(
                        begin: const Offset(1, 1), end: const Offset(0.9, 0.9))
                  else
                    // START BUTTON
                    Padding(
                      padding: const EdgeInsets.only(bottom: 20),
                      child: ElevatedButton.icon(
                          onPressed: _initCamera,
                          icon:
                              const Icon(Icons.camera_alt, color: Colors.white),
                          label: Text("OPEN LENS",
                              style: GoogleFonts.outfit(
                                  fontWeight: FontWeight.bold, fontSize: 16)),
                          style: ElevatedButton.styleFrom(
                              backgroundColor: _sageGreen,
                              foregroundColor: Colors.white,
                              elevation: 5,
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 40, vertical: 20),
                              shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(40)))),
                    ),

                  const SizedBox(height: 30),
                ],
              ),
            ),
          )
        ],
      ),
    );
  }
}
