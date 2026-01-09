class UserProfile {
  final String id;
  final String name;
  final bool isPet;
  final List<String> allergies; // e.g. "Peanuts", "Gluten"
  final List<String> medications; // e.g. "Statins"
  final List<String> conditions; // e.g. "Diabetes"

  UserProfile({
    required this.id,
    required this.name,
    this.isPet = false,
    this.allergies = const [],
    this.medications = const [],
    this.conditions = const [],
  });

  // Convert to JSON for sending to Backend
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'is_pet': isPet,
      'allergies': allergies,
      'medications': medications,
      'conditions': conditions,
    };
  }

  // Factory for default profiles
  static List<UserProfile> getDefaults() {
    return [
      UserProfile(
        id: 'user_me',
        name: 'Me (Mikasa)',
        conditions: ['Sensitive Skin'],
      ),
      UserProfile(
        id: 'pet_xiaobai',
        name: 'Xiaobai (Dog)',
        isPet: true,
        allergies: ['Xylitol', 'Chocolate', 'Grapes', 'Onions'], // Dog Toxins
      ),
      UserProfile(
        id: 'pet_mimi',
        name: 'Mimi (Cat)',
        isPet: true,
        allergies: ['Lilies', 'Essential Oils', 'Permethrin', 'Chocolate'], // Cat Toxins
      ),
    ];
  }
}
