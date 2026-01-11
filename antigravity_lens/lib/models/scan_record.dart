class ScanRecord {
  final String id;
  final String date;
  final String result;
  final bool
      isSafe; // Simple guess based on text analysis? Or just store raw text.

  ScanRecord({
    required this.id,
    required this.date,
    required this.result,
    this.isSafe = true,
  });

  Map<String, dynamic> toJson() => {
        'id': id,
        'date': date,
        'result': result,
        'isSafe': isSafe,
      };

  factory ScanRecord.fromJson(Map<String, dynamic> json) {
    return ScanRecord(
      id: json['id'],
      date: json['date'],
      result: json['result'],
      isSafe: json['isSafe'] ?? true,
    );
  }
}
