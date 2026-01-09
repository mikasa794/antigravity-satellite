import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_markdown/flutter_markdown.dart';

class TruthCard extends StatelessWidget {
  final String resultText;
  final VoidCallback onClose;

  const TruthCard({
    super.key,
    required this.resultText,
    required this.onClose,
  });

  // Helper to determine status color/icon
  // Logic: AI usually replies with "🟢 SAFE", "⚠️ CAUTION", or "🛑 AVOID"
  _Status get _status {
    if (resultText.contains("🛑") || resultText.toUpperCase().contains("AVOID") || resultText.toUpperCase().contains("DANGER")) {
      return _Status.danger;
    } else if (resultText.contains("⚠️") || resultText.toUpperCase().contains("CAUTION") || resultText.toUpperCase().contains("WARNING")) {
      return _Status.warning;
    } else if (resultText.contains("🟢") || resultText.toUpperCase().contains("SAFE")) {
      return _Status.safe;
    }
    return _Status.neutral;
  }

  @override
  Widget build(BuildContext context) {
    final status = _status;
    Color themeColor;
    IconData themeIcon;
    String title;

    switch (status) {
      case _Status.safe:
        themeColor = const Color(0xFF00E676); // Bright Green
        themeIcon = Icons.check_circle_outline;
        title = "SAFE";
        break;
      case _Status.warning:
        themeColor = const Color(0xFFFFEA00); // Bright Yellow
        themeIcon = Icons.warning_amber_rounded;
        title = "CAUTION";
        break;
      case _Status.danger:
        themeColor = const Color(0xFFFF1744); // Bright Red
        themeIcon = Icons.block;
        title = "AVOID";
        break;
      default:
        themeColor = Colors.white;
        themeIcon = Icons.info_outline;
        title = "INSIGHT";
    }

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A1A), // Dark Grey base
        borderRadius: const BorderRadius.vertical(top: Radius.circular(32)),
        border: Border(
          top: BorderSide(color: themeColor.withOpacity(0.5), width: 2),
        ),
        boxShadow: [
          BoxShadow(
            color: themeColor.withOpacity(0.2),
            blurRadius: 40,
            spreadRadius: 5,
          )
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header (Handle)
          Center(
            child: Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.only(bottom: 20),
              decoration: BoxDecoration(
                color: Colors.grey[800],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),

          // Verdict Header
          Row(
            children: [
              Icon(themeIcon, color: themeColor, size: 32),
              const SizedBox(width: 16),
              Text(
                title,
                style: GoogleFonts.outfit(
                  color: themeColor,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                ),
              ),
              const Spacer(),
              IconButton(
                icon: const Icon(Icons.close, color: Colors.grey),
                onPressed: onClose,
              )
            ],
          ),

          const SizedBox(height: 24),
          const Divider(color: Colors.white12),
          const SizedBox(height: 16),

          // Content (Scrollable)
          Flexible(
            child: SingleChildScrollView(
              child: MarkdownBody(
                data: resultText,
                styleSheet: MarkdownStyleSheet(
                  p: GoogleFonts.outfit(
                    color: Colors.white.withOpacity(0.9),
                    fontSize: 16,
                    height: 1.6,
                  ),
                  strong: GoogleFonts.outfit(
                    color: themeColor,
                    fontWeight: FontWeight.bold,
                  ),
                  h1: GoogleFonts.outfit(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                  h2: GoogleFonts.outfit(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                  h3: GoogleFonts.outfit(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                  listBullet: TextStyle(color: themeColor),
                ),
              ),
            ),
          ),
          
          const SizedBox(height: 20),
          
          // Action Button
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: themeColor.withOpacity(0.2),
              foregroundColor: themeColor,
              padding: const EdgeInsets.symmetric(vertical: 16),
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
                side: BorderSide(color: themeColor.withOpacity(0.5)),
              ),
            ),
            onPressed: onClose,
            child: Text(
              "UNDERSTOOD", 
              style: const TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1),
            ),
          ),
        ],
      ),
    );
  }
}

enum _Status { safe, warning, danger, neutral }
