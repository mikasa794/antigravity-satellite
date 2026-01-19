import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:camera/camera.dart'; // For XFile
import 'package:flutter/foundation.dart'; // For kIsWeb
import '../models/profile.dart';
import 'package:http_parser/http_parser.dart';

class ApiService {
  // Cloud Backend (Production/Web)
  static const String _cloudUrl = 'https://antigravity-satellite.onrender.com';

  // Local Backend (Android Emulator loopback)
  static const String _localAndroidUrl = 'http://10.0.2.2:5000';

  // Local Backend (iOS Simulator / Desktop loopback)
  static const String _localDesktopUrl = 'http://127.0.0.1:5000';

  static String get baseUrl {
    if (kIsWeb) return _cloudUrl;
    if (defaultTargetPlatform == TargetPlatform.android)
      return _localAndroidUrl;
    return _localDesktopUrl;
  }

  static Future<String> scanImage(XFile imageFile, List<UserProfile> profiles,
      UserProfile selectedProfile) async {
    final uri = Uri.parse('$baseUrl/api/scan');

    try {
      final request = http.MultipartRequest('POST', uri);

      // 1. Add Image (Using bytes ensures compatibility across Web/Mobile)
      final bytes = await imageFile.readAsBytes();

      request.files.add(http.MultipartFile.fromBytes(
        'image',
        bytes,
        filename: imageFile.name,
        contentType: MediaType('image', 'jpeg'), // Assuming JPEG from camera
      ));

      // 2. Add Profiles (Serialize to JSON string)
      final profilesJson = jsonEncode(profiles.map((p) => p.toJson()).toList());
      request.fields['profiles'] = profilesJson;

      // 3. Add Selected Profile ID
      request.fields['selected_profile_id'] = selectedProfile.id;

      // 4. Send
      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['result'] ?? "No result returned.";
      } else {
        return "Error: ${response.statusCode} - ${response.body}";
      }
    } catch (e) {
      return "Connection Failed: $e";
    }
  }
}
