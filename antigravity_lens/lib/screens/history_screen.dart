import 'package:flutter/material.dart';
import 'package:antigravity_lens/services/history_service.dart';
import 'package:antigravity_lens/models/scan_record.dart';
import 'package:antigravity_lens/widgets/truth_card.dart';
import 'package:flutter_animate/flutter_animate.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<ScanRecord> records = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    final data = await HistoryService.getRecords();
    if (mounted) {
      setState(() {
        records = data;
        isLoading = false;
      });
    }
  }

  void _showDetail(ScanRecord record) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => TruthCard(
        resultText: record.result,
        onClose: () => Navigator.pop(context),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        title: const Text("MEMORY LANE",
            style:
                TextStyle(color: Colors.white, letterSpacing: 2, fontSize: 16)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline, color: Colors.white54),
            onPressed: () async {
              await HistoryService.clearHistory();
              _loadHistory();
            },
          )
        ],
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator(color: Colors.white))
          : records.isEmpty
              ? Center(
                  child: Text("NO MEMORIES YET",
                      style: TextStyle(
                          color: Colors.white.withOpacity(0.3),
                          letterSpacing: 2)))
              : ListView.builder(
                  padding: const EdgeInsets.all(20),
                  itemCount: records.length,
                  itemBuilder: (context, index) {
                    final record = records[index];
                    return GestureDetector(
                      onTap: () => _showDetail(record),
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.05),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.white10),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              record.date,
                              style: TextStyle(
                                  color: Colors.white.withOpacity(0.4),
                                  fontSize: 12),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              record.result,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                  color: Colors.white, fontSize: 14),
                            ),
                          ],
                        ),
                      )
                          .animate()
                          .fadeIn(delay: (50 * index).ms)
                          .slideY(begin: 0.1),
                    );
                  },
                ),
    );
  }
}
