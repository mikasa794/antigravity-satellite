import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/profile.dart';

class ApiService {
  // Use 10.0.2.2 for Android Emulator to access localhost.
  static const String _baseUrl = 'http://10.0.2.2:5000'; 

  static Future<String> scanImage(String imagePath, List<UserProfile> profiles) async {
    final uri = Uri.parse('$_baseUrl/api/scan');
    
    try {
      final request = http.MultipartRequest('POST', uri);
      
      // 1. Add Image
      request.files.add(await http.MultipartFile.fromPath('image', imagePath));
      
      // 2. Add Profiles (Serialize to JSON string)
      final profilesJson = jsonEncode(profiles.map((p) => p.toJson()).toList());
      request.fields['profiles'] = profilesJson;

      // 3. Send
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
