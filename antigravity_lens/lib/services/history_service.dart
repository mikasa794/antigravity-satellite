import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:antigravity_lens/models/scan_record.dart';

class HistoryService {
  static const String key = 'scan_history';

  static Future<void> saveRecord(ScanRecord record) async {
    final prefs = await SharedPreferences.getInstance();
    List<String> history = prefs.getStringList(key) ?? [];

    // Convert to JSON String
    String jsonStr = jsonEncode(record.toJson());

    // Add to top of list
    history.insert(0, jsonStr);

    // Optional: Limit history to last 50 items to save space
    if (history.length > 50) {
      history = history.sublist(0, 50);
    }

    await prefs.setStringList(key, history);
  }

  static Future<List<ScanRecord>> getRecords() async {
    final prefs = await SharedPreferences.getInstance();
    List<String> history = prefs.getStringList(key) ?? [];

    return history.map((str) => ScanRecord.fromJson(jsonDecode(str))).toList();
  }

  static Future<void> clearHistory() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(key);
  }
}
