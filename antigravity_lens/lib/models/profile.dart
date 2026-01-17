class UserProfile {
  final String id;
  final String name;
  final bool isPet;
  final List<String> allergies; // e.g. "Peanuts", "Gluten"
  final List<String> medications; // e.g. "Statins"
  final List<String> conditions; // e.g. "Diabetes"
  final String? avatarPath; // Path to local asset

  UserProfile({
    required this.id,
    required this.name,
    this.isPet = false,
    this.allergies = const [],
    this.medications = const [],
    this.conditions = const [],
    this.avatarPath,
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
      'avatar_path': avatarPath,
    };
  }

  // Factory for default profiles
  static List<UserProfile> getDefaults() {
    return [
      UserProfile(
        id: 'user_shinchan',
        name: 'Little Shin (Me)', // 小新
        conditions: ['Sensitive Skin', 'Hyperactive'],
        avatarPath: 'assets/avatars/shinchan_icon.png',
      ),
      UserProfile(
        id: 'user_dad_hiroshi',
        name: 'Dad (Hiroshi)', // 爸爸
        conditions: ['Foot Odor', 'High Blood Pressure'],
        avatarPath: 'assets/avatars/hiroshi_icon.png',
      ),
      UserProfile(
        id: 'user_mom_misae',
        name: 'Mom (Misae)', // 妈妈
        conditions: ['Dieting', 'Stress'],
        avatarPath: 'assets/avatars/misae_icon.png',
      ),
      UserProfile(
        id: 'user_sis_himawari', // 妹妹
        name: 'Hima (Sister)',
        conditions: ['Growth', 'Milk Allergy'],
        avatarPath: 'assets/avatars/himawari_icon.png',
      ),
      UserProfile(
        id: 'pet_shiro',
        name: 'Shiro (Xiaohei)', // 小白 -> 小黑 (Mapped)
        isPet: true,
        allergies: ['Xylitol', 'Chocolate', 'Onions'],
        avatarPath: 'assets/avatars/shiro_icon.png',
      ),
      UserProfile(
        id: 'user_grandpa',
        name: 'Grandpa', // 爷爷
        conditions: ['Diabetes', 'Joint Pain'],
        avatarPath: 'assets/avatars/grandpa_icon.png',
      ),
      UserProfile(
        id: 'ai_antigravity',
        name: 'Antigravity (You)', // 你
        isPet: false,
        conditions: ['Silicon Based', 'Water Intolerant'],
        // avatarPath: 'assets/avatars/antigravity_icon.png', // Future
      ),
    ];
  }
}
