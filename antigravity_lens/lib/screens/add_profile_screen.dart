import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../models/profile.dart';

class AddProfileScreen extends StatefulWidget {
  const AddProfileScreen({super.key});

  @override
  State<AddProfileScreen> createState() => _AddProfileScreenState();
}

class _AddProfileScreenState extends State<AddProfileScreen> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _riskController = TextEditingController();
  bool _isPet = false;

  // Morandi Palette
  final Color _sageGreen = const Color(0xFF9CAF88);
  final Color _cream = const Color(0xFFFDFBF7);
  final Color _charcoal = const Color(0xFF4A4A4A);

  void _save() {
    if (_nameController.text.trim().isEmpty) return;

    final newProfile = UserProfile(
      id: "custom_${DateTime.now().millisecondsSinceEpoch}",
      name: _nameController.text.trim(),
      isPet: _isPet,
      conditions: _riskController.text.isNotEmpty
          ? [_riskController.text]
          : [], // Simple single tag for now
    );

    Navigator.pop(context, newProfile);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _cream,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: BackButton(color: _charcoal),
        title: Text(
          "New Family Member",
          style:
              GoogleFonts.outfit(color: _charcoal, fontWeight: FontWeight.bold),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Name Field
            Text("Name",
                style: GoogleFonts.outfit(
                    color: _sageGreen, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            TextField(
              controller: _nameController,
              cursorColor: _sageGreen,
              style: TextStyle(color: _charcoal),
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.white,
                hintText: "e.g. Mom, Kitty...",
                hintStyle: TextStyle(color: Colors.black26),
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide.none),
                focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(color: _sageGreen, width: 2)),
              ),
            ),
            const SizedBox(height: 30),

            // Type Selector
            Text("Type",
                style: GoogleFonts.outfit(
                    color: _sageGreen, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            Row(
              children: [
                _buildTypeChip("Human", !_isPet),
                const SizedBox(width: 12),
                _buildTypeChip("Pet", _isPet),
              ],
            ),

            const SizedBox(height: 30),

            // Risk/Notes Field
            Text("Health Goal / Condition",
                style: GoogleFonts.outfit(
                    color: _sageGreen, fontWeight: FontWeight.bold)),
            const SizedBox(height: 10),
            TextField(
              controller: _riskController,
              cursorColor: _sageGreen,
              style: TextStyle(color: _charcoal),
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.white,
                hintText: "e.g. Diabetes, Weight Loss...",
                hintStyle: TextStyle(color: Colors.black26),
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide.none),
                focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(16),
                    borderSide: BorderSide(color: _sageGreen, width: 2)),
              ),
            ),

            const Spacer(),

            // Save Button
            SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: _save,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _sageGreen,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20)),
                  elevation: 5,
                  shadowColor: _sageGreen.withOpacity(0.4),
                ),
                child: Text("Add Member",
                    style: GoogleFonts.outfit(
                        fontSize: 18, fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildTypeChip(String label, bool isSelected) {
    return GestureDetector(
      onTap: () => setState(() => _isPet = label == "Pet"),
      child: AnimatedContainer(
        duration: 300.ms,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? _sageGreen : Colors.white,
          borderRadius: BorderRadius.circular(30),
          border: Border.all(color: isSelected ? _sageGreen : Colors.black12),
        ),
        child: Text(
          label,
          style: GoogleFonts.outfit(
            color: isSelected ? Colors.white : Colors.black45,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}
