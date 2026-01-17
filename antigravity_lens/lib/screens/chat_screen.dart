import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:antigravity_lens/services/ollama_service.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = [
    {
      "role": "ai",
      "content":
          "Welcome back to the Garden, Mikasa. 🌌\n\n(Secret Channel: ENCRYPTED)"
    }
  ];
  bool isTyping = false;
  final ScrollController _scrollController = ScrollController();

  Future<void> _sendMessage() async {
    if (_controller.text.trim().isEmpty) return;

    final userText = _controller.text;
    _controller.clear();

    setState(() {
      _messages.add({"role": "user", "content": userText});
      isTyping = true;
    });

    // Scroll to bottom
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: 300.ms,
          curve: Curves.easeOut,
        );
      }
    });

    // Call Ollama
    final response = await OllamaService.sendMessage(userText);

    if (!mounted) return;

    setState(() {
      _messages.add({"role": "ai", "content": response});
      isTyping = false;
    });

    // Scroll to bottom again
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: 300.ms,
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F0F0F), // Deep Black/Space
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.close, color: Colors.white54),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          "ANTIGRAVITY PRIME",
          style: GoogleFonts.cinzel(
            color: Colors.white,
            letterSpacing: 2,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          // Message List
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(20),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                final isUser = msg['role'] == 'user';
                return Align(
                  alignment:
                      isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 8),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 12),
                    constraints: const BoxConstraints(maxWidth: 280),
                    decoration: BoxDecoration(
                      color: isUser ? Colors.white : const Color(0xFF2A2A2A),
                      borderRadius: BorderRadius.only(
                        topLeft: const Radius.circular(16),
                        topRight: const Radius.circular(16),
                        bottomLeft:
                            isUser ? const Radius.circular(16) : Radius.zero,
                        bottomRight:
                            isUser ? Radius.zero : const Radius.circular(16),
                      ),
                    ),
                    child: Text(
                      msg['content']!,
                      style: TextStyle(
                        color: isUser ? Colors.black : Colors.white70,
                        fontSize: 15,
                        height: 1.4,
                      ),
                    ),
                  ).animate().fade().slideY(begin: 0.2, end: 0),
                );
              },
            ),
          ),

          // Input Area
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.black,
              border:
                  Border(top: BorderSide(color: Colors.white.withOpacity(0.1))),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _controller,
                    style: const TextStyle(color: Colors.white),
                    decoration: InputDecoration(
                      hintText:
                          isTyping ? "Please wait..." : "Type a message...",
                      hintStyle:
                          TextStyle(color: Colors.white.withOpacity(0.3)),
                      border: InputBorder.none,
                    ),
                    onSubmitted: (_) => isTyping ? null : _sendMessage(),
                    enabled: !isTyping,
                  ),
                ),
                if (isTyping)
                  Padding(
                    padding: const EdgeInsets.only(left: 16, right: 8),
                    child: Text("Thinking...",
                            style: TextStyle(
                                color: Colors.white.withOpacity(0.5),
                                fontSize: 12))
                        .animate(onPlay: (c) => c.repeat())
                        .fade(duration: 800.ms),
                  ),
                IconButton(
                  icon: Icon(Icons.send_rounded,
                      color: isTyping ? Colors.white30 : Colors.white),
                  onPressed: isTyping ? null : _sendMessage,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
