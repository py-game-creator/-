import json
import os
import hashlib
import base64
from getpass import getpass
from typing import Dict, Optional, List
from datetime import datetime
import random
import time

# ========== 游戏配置 ==========
SAVE_FILE = "element_save.json"
ADMIN_USER = "Admin_8888"
ADMIN_PASS = "Admin_8888"

# 可选元素
NORMAL_ELEMENTS = ["金", "木", "水", "火", "土", "风", "冰", "雷", "暗", "光"]
HIDDEN_ELEMENT = "全元素"

# 元素克制关系表
ELEMENT_COUNTER = {
    "金": ["木"], "木": ["土"], "土": ["水"], "水": ["火"], "火": ["金"],
    "风": ["雷"], "雷": ["水"], "冰": ["火", "风"],
    "暗": ["光"], "光": ["暗"],
    "全元素": []
}

# 元素相生关系
ELEMENT_BOOST = {
    "金": "水", "水": "木", "木": "火", "火": "土", "土": "金",
    "风": "雷", "雷": "风", "冰": "水",
    "暗": "光", "光": "暗",
    "全元素": "全元素"
}

# 元素描述
ELEMENT_DESCRIPTIONS = {
    "金": "锋锐之金，无坚不摧",
    "木": "生机之木，生生不息",
    "水": "柔韧之水，以柔克刚",
    "火": "爆裂之火，焚尽万物",
    "土": "厚重之土，稳如磐石",
    "风": "疾速之风，无形无相",
    "冰": "寒冰之力，冻结一切",
    "雷": "雷霆之威，震慑九天",
    "暗": "深渊之暗，吞噬光明",
    "光": "神圣之光，驱散黑暗",
    "全元素": "混沌之源，万法归一"
}

# ========== 组合技系统 ==========
COMBO_SKILLS = {
    ("金", "水"): {"name": "寒冰剑气", "description": "金生水，剑气凝冰", "damage": 180, "effect": "冻结敌人1回合", "mp_cost": 30},
    ("水", "木"): {"name": "生命之泉", "description": "水生木，治愈万物", "damage": 0, "effect": "恢复50%HP", "mp_cost": 25},
    ("木", "火"): {"name": "烈焰风暴", "description": "木生火，焚天煮海", "damage": 200, "effect": "持续灼烧3回合", "mp_cost": 35},
    ("火", "土"): {"name": "熔岩铠甲", "description": "火生土，熔岩护体", "damage": 0, "effect": "防御力提升50%", "mp_cost": 20},
    ("土", "金"): {"name": "金刚不坏", "description": "土生金，坚不可摧", "damage": 0, "effect": "无敌1回合", "mp_cost": 40},
    ("风", "雷"): {"name": "雷霆风暴", "description": "风雷相生，天罚降临", "damage": 220, "effect": "麻痹敌人2回合", "mp_cost": 35},
    ("光", "暗"): {"name": "混沌审判", "description": "光暗交融，归于混沌", "damage": 250, "effect": "无视防御", "mp_cost": 50},
    ("冰", "水"): {"name": "绝对零度", "description": "冰水相融，冻结时空", "damage": 160, "effect": "冻结全体敌人", "mp_cost": 30},
}

# ========== 共鸣加成系统 ==========
RESONANCE_SETS = {
    "五行归一": {"elements": ["金", "木", "水", "火", "土"], "bonus": {"attack": 50, "defense": 50, "hp": 500, "special": "五行轮转：每回合恢复10%HP"}, "description": "集齐五行元素，达成完美循环"},
    "光暗同源": {"elements": ["光", "暗"], "bonus": {"attack": 80, "defense": 30, "hp": 300, "special": "混沌之力：技能伤害+30%"}, "description": "光与暗的完美平衡"},
    "风雷共鸣": {"elements": ["风", "雷"], "bonus": {"attack": 60, "speed": 40, "hp": 200, "special": "疾风迅雷：必定先手攻击"}, "description": "风驰电掣，迅如雷霆"},
    "冰火两重": {"elements": ["冰", "火"], "bonus": {"attack": 70, "defense": 20, "hp": 250, "special": "冰火交织：攻击附带冰冻/灼烧"}, "description": "冰与火的交响曲"},
}

# ========== 加密系统 ==========
class SimpleEncryption:
    def __init__(self, username: str):
        self.username = username
        self.key = hashlib.pbkdf2_hmac('sha256', username.encode(), b'salt', 100000, dklen=32)
    
    def encrypt_element(self, element: str) -> str:
        if not element: return ""
        data = datetime.now().microsecond.to_bytes(4, 'big') + element.encode()
        encrypted = bytes([b ^ self.key[i % len(self.key)] for i, b in enumerate(data)])
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt_element(self, encrypted_element: str) -> str:
        if not encrypted_element: return ""
        try:
            encrypted = base64.urlsafe_b64decode(encrypted_element.encode())
            decrypted = bytes([b ^ self.key[i % len(self.key)] for i, b in enumerate(encrypted)])
            return decrypted[4:].decode()
        except:
            return ""

# ========== 登录系统 ==========
class LoginSystem:
    def __init__(self):
        self.current_user = None
        self.is_admin = False
    
    def login(self) -> bool:
        print("\n" + "="*40)
        print("        元素觉醒 · 登录系统")
        print("="*40)
        username = input("用户名: ").strip()
        password = getpass("密码: ")
        if username == ADMIN_USER and password == ADMIN_PASS:
            self.current_user = username
            self.is_admin = True
            print(f"\n✨ 管理员 {username} 登录成功！")
            return True
        data = self._load_save_data()
        if username in data.get("users", {}):
            stored_hash = data["users"][username]["password_hash"]
            if hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex() == stored_hash:
                self.current_user = username
                self.is_admin = False
                print(f"\n✅ 欢迎回来，{username}！")
                return True
            else:
                print("\n❌ 密码错误。")
                return False
        else:
            print(f"\n📝 新用户 '{username}'，正在自动注册...")
            if "users" not in data: data["users"] = {}
            data["users"][username] = {
                "password_hash": hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex(),
                "element_encrypted": "", "allies": [],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self._save_save_data(data)
            self.current_user = username
            self.is_admin = False
            print(f"✅ 注册成功，{username}！")
            return True
    
    def _load_save_data(self) -> dict:
        if not os.path.exists(SAVE_FILE): return {"users": {}}
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except:
            return {"users": {}}
    
    def _save_save_data(self, data: dict):
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# ========== 存档系统 ==========
class SaveSystem:
    def __init__(self):
        self.data = self._load()
    
    def _load(self) -> dict:
        if not os.path.exists(SAVE_FILE): return {"users": {}}
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except:
            return {"users": {}}
    
    def _save(self):
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    
    def get_element(self, username: str) -> Optional[str]:
        encrypted = self.data.get("users", {}).get(username, {}).get("element_encrypted", "")
        if not encrypted: return None
        return SimpleEncryption(username).decrypt_element(encrypted)
    
    def set_element(self, username: str, element: str):
        if username not in self.data.get("users", {}): return
        encrypted = SimpleEncryption(username).encrypt_element(element)
        self.data["users"][username]["element_encrypted"] = encrypted
        self._save()
    
    def get_allies(self, username: str) -> List[str]:
        return self.data.get("users", {}).get(username, {}).get("allies", [])
    
    def add_ally(self, username: str, element: str) -> bool:
        if username not in self.data.get("users", {}): return False
        allies = self.get_allies(username)
        if element not in allies and len(allies) < 4:
            allies.append(element)
            self.data["users"][username]["allies"] = allies
            self._save()
            return True
        return False

# ========== 组合技系统类 ==========
class ComboSystem:
    def __init__(self, player_element: str, allies: List[str]):
        self.player_element = player_element
        self.allies = allies
    
    def get_available_combos(self) -> List[Dict]:
        available = []
        all_elements = [self.player_element] + self.allies
        for i, elem1 in enumerate(all_elements):
            for elem2 in all_elements[i+1:]:
                for key in [(elem1, elem2), (elem2, elem1)]:
                    if key in COMBO_SKILLS:
                        skill = COMBO_SKILLS[key].copy()
                        skill["elements"] = f"{key[0]}+{key[1]}"
                        available.append(skill)
                        break
        return available

# ========== 共鸣系统类 ==========
class ResonanceSystem:
    def __init__(self, player_element: str, allies: List[str]):
        self.all_elements = [player_element] + allies
    
    def calculate_bonus_stats(self) -> Dict:
        total = {"attack": 0, "defense": 0, "hp": 0, "speed": 0, "specials": []}
        for set_data in RESONANCE_SETS.values():
            if self._check_set(set_data["elements"]):
                bonus = set_data["bonus"]
                for k in ["attack", "defense", "hp", "speed"]:
                    if k in bonus: total[k] += bonus[k]
                if "special" in bonus: total["specials"].append(bonus["special"])
        return total
    
    def _check_set(self, required: List[str]) -> bool:
        elems = self.all_elements.copy()
        for req in required:
            if req in elems: elems.remove(req)
            else: return False
        return True

# ========== 玩家战斗属性 ==========
class PlayerCombatStats:
    def __init__(self, element: str, allies: List[str]):
        bonus = ResonanceSystem(element, allies).calculate_bonus_stats()
        self.max_hp = 500 + bonus.get("hp", 0)
        self.current_hp = self.max_hp
        self.max_mp = 100
        self.current_mp = 100
        self.base_attack = 80 + bonus.get("attack", 0)
        self.base_defense = 40 + bonus.get("defense", 0)
        self.speed = 100 + bonus.get("speed", 0)
    
    def take_damage(self, damage: int) -> int:
        reduced = max(1, damage - self.base_defense // 2)
        self.current_hp = max(0, self.current_hp - reduced)
        return reduced
    
    def heal(self, amount: int):
        self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def use_mp(self, cost: int) -> bool:
        if self.current_mp >= cost:
            self.current_mp -= cost
            return True
        return False
    
    def recover_mp(self, amount: int):
        self.current_mp = min(self.max_mp, self.current_mp + amount)
    
    def is_alive(self) -> bool:
        return self.current_hp > 0

# ========== Boss 彼岸双生 ==========
class BossManjusaka:
    def __init__(self):
        self.name = "曼陀罗华·曼珠沙华"
        self.title = "彼岸双生"
        self.max_hp = 2000
        self.current_hp = 2000
        self.skill2_damage_boost = 0
        self.skills = {
            1: {"name": "彼岸·轮回之愈", "type": "heal"},
            2: {"name": "冥府·死亡绽放", "type": "damage", "base_damage": 50},
            3: {"name": "血祭·花开彼岸", "type": "sacrifice"}
        }
    
    def take_damage(self, damage: int) -> int:
        self.current_hp = max(0, self.current_hp - damage)
        return damage
    
    def heal(self, amount: int):
        self.current_hp = min(self.max_hp, self.current_hp + amount)
    
    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def use_skill_1(self) -> Dict:
        heal_amount = int(self.max_hp * 0.8)
        self.heal(heal_amount)
        return {"skill_name": self.skills[1]["name"], "effect": "heal", "value": heal_amount, "message": f"彼岸花海绽放，Boss恢复了 {heal_amount} 点生命！"}
    
    def use_skill_2(self) -> Dict:
        total_damage = int(self.skills[2]["base_damage"] * (1 + self.skill2_damage_boost))
        return {"skill_name": self.skills[2]["name"], "effect": "damage", "value": total_damage, "message": f"血红色的彼岸花绽放，造成 {total_damage} 点伤害！"}
    
    def use_skill_3(self) -> Dict:
        sacrifice = int(self.current_hp * 0.7)
        self.current_hp -= sacrifice
        self.skill2_damage_boost += 0.3
        return {"skill_name": self.skills[3]["name"], "effect": "sacrifice", "value": sacrifice, "boost": self.skill2_damage_boost, "message": f"Boss献祭了 {sacrifice} 点生命！死亡绽放的伤害提升了30%！"}
    
    def choose_action(self, player_hp_percent: float) -> Dict:
        if self.current_hp < self.max_hp * 0.3 and random.random() < 0.6:
            return self.use_skill_1()
        if self.skill2_damage_boost < 0.9 and self.current_hp > self.max_hp * 0.4 and random.random() < 0.5:
            return self.use_skill_3()
        if player_hp_percent > 0.5 and self.current_hp > self.max_hp * 0.5 and random.random() < 0.4:
            return self.use_skill_3()
        return self.use_skill_2()
    
    def show_status(self):
        hp_percent = (self.current_hp / self.max_hp) * 100
        hp_bar = "█" * int(hp_percent / 5) + "░" * (20 - int(hp_percent / 5))
        print(f"\n{'='*50}")
        print(f"  {self.name} · {self.title}")
        print(f"  HP: {self.current_hp}/{self.max_hp} [{hp_bar}] {hp_percent:.1f}%")
        if self.skill2_damage_boost > 0:
            print(f"  ⚠️ 死亡绽放强化: +{int(self.skill2_damage_boost * 100)}% 伤害")
        print(f"{'='*50}")

# ========== 战斗系统 ==========
class BattleSystem:
    def __init__(self, player_stats: PlayerCombatStats, player_element: str, allies: List[str]):
        self.player = player_stats
        self.player_element = player_element
        self.allies = allies
        self.boss = BossManjusaka()
        self.turn_count = 0
        self.combo_system = ComboSystem(player_element, allies)
        self.battle_log = []
        self.player_defense_boost = 0
        self.player_defense_boost_turns = 0
        self.player_invincible = 0
        self.boss_frozen = 0
        self.boss_paralyzed = 0
        self.boss_burning = 0
    
    def player_attack(self) -> Dict:
        damage = self.player.base_attack + random.randint(-10, 10)
        actual = self.boss.take_damage(damage)
        return {"type": "attack", "damage": actual, "message": f"你对Boss造成了 {actual} 点伤害！"}
    
    def player_defend(self) -> Dict:
        self.player_defense_boost = 50
        self.player_defense_boost_turns = 2
        self.player.recover_mp(20)
        return {"type": "defend", "message": "你进入防御姿态，防御力提升50%，恢复了20点MP！"}
    
    def player_use_combo(self, combo_index: int) -> Dict:
        combos = self.combo_system.get_available_combos()
        if combo_index < 0 or combo_index >= len(combos):
            return {"type": "failed", "message": "组合技不存在！"}
        combo = combos[combo_index]
        if not self.player.use_mp(combo['mp_cost']):
            return {"type": "failed", "message": f"MP不足！需要{combo['mp_cost']}MP"}
        msg = f"使用【{combo['name']}】！"
        if combo['damage'] > 0:
            actual = self.boss.take_damage(combo['damage'])
            msg += f"造成 {actual} 点伤害！"
        if "冻结" in combo['effect']:
            self.boss_frozen = 1 if "全体" not in combo['effect'] else 2
            msg += f" Boss被冻结{self.boss_frozen}回合！"
        elif "恢复50%" in combo['effect']:
            heal = int(self.player.max_hp * 0.5)
            self.player.heal(heal)
            msg += f" 恢复了 {heal} 点生命！"
        elif "防御力提升" in combo['effect']:
            self.player_defense_boost = 50
            self.player_defense_boost_turns = 3
            msg += " 防御力提升50%！"
        elif "无敌" in combo['effect']:
            self.player_invincible = 1
            msg += " 获得无敌效果！"
        elif "麻痹" in combo['effect']:
            self.boss_paralyzed = 2
            msg += " Boss被麻痹2回合！"
        elif "灼烧" in combo['effect']:
            self.boss_burning = 3
            msg += " Boss被灼烧3回合！"
        return {"type": "combo", "message": msg}
    
    def player_turn(self, action: str, action_data: int = None) -> Dict:
        if action == "attack": result = self.player_attack()
        elif action == "defend": result = self.player_defend()
        elif action == "combo": result = self.player_use_combo(action_data)
        else:
            self.player.heal(30)
            self.player.recover_mp(20)
            result = {"type": "recover", "message": "你集中精神，恢复了30 HP和20 MP！"}
        self.player.recover_mp(10)
        self._update_status()
        return result
    
    def boss_turn(self) -> Dict:
        if self.boss_frozen > 0:
            self.boss_frozen -= 1
            return {"type": "frozen", "message": "Boss被冻结，无法行动！"}
        if self.boss_paralyzed > 0:
            self.boss_paralyzed -= 1
            if random.random() < 0.5:
                return {"type": "paralyzed", "message": "Boss被麻痹，无法行动！"}
        action = self.boss.choose_action(self.player.current_hp / self.player.max_hp)
        if action["effect"] == "damage":
            damage = action["value"]
            if self.player_invincible > 0:
                return {"type": "invincible", "message": f"无敌效果抵御了 {damage} 点伤害！"}
            if self.player_defense_boost_turns > 0:
                damage = int(damage * 0.5)
            actual = self.player.take_damage(damage)
            return {"type": "damage", "skill_name": action["skill_name"], "damage": actual, "message": f"Boss使用【{action['skill_name']}】！{action['message']}"}
        return action
    
    def _update_status(self):
        if self.player_defense_boost_turns > 0:
            self.player_defense_boost_turns -= 1
            if self.player_defense_boost_turns == 0: self.player_defense_boost = 0
        if self.player_invincible > 0: self.player_invincible -= 1
        if self.boss_burning > 0:
            self.boss.take_damage(30)
            self.boss_burning -= 1
            self.battle_log.append("灼烧效果造成 30 点伤害！")
    
    def show_status(self):
        php = (self.player.current_hp / self.player.max_hp) * 100
        pmp = (self.player.current_mp / self.player.max_mp) * 100
        print(f"\n{'='*50}")
        print(f"  🎮 玩家 HP: {self.player.current_hp}/{self.player.max_hp} [{php:.1f}%]")
        print(f"      MP: {self.player.current_mp}/{self.player.max_mp} [{pmp:.1f}%]")
        self.boss.show_status()
        if self.battle_log:
            print(f"\n📜 {self.battle_log[-1]}")
        print(f"{'='*50}")
    
    def start_battle(self) -> bool:
        print("\n" + "⚔️"*25)
        print("     彼岸之战 · 开始")
        print("⚔️"*25)
        while self.player.is_alive() and self.boss.is_alive():
            self.turn_count += 1
            print(f"\n─── 第 {self.turn_count} 回合 ───")
            self.show_status()
            
            # 显示菜单
            print("\n🎯 行动:")
            print("  1. 普通攻击")
            print("  2. 防御 (提升防御，恢复MP)")
            print("  4. 集中恢复 (恢复HP和MP)")
            
            # 显示组合技
            combos = self.combo_system.get_available_combos()
            if combos:
                print("\n  组合技:")
                for i, c in enumerate(combos):
                    print(f"    c{i+1}. {c['name']} (MP:{c['mp_cost']}) - {c['description']}")
            else:
                print("\n  (暂无可用组合技，招募伙伴可解锁)")
            
            choice = input("\n请选择: ").strip().lower()
            
            # 处理玩家选择
            if choice == "1":
                result = self.player_turn("attack")
            elif choice == "2":
                result = self.player_turn("defend")
            elif choice == "4":
                result = self.player_turn("recover")
            elif choice.startswith("c"):
                try:
                    idx = int(choice[1:]) - 1
                    result = self.player_turn("combo", idx)
                except:
                    print("❌ 无效的组合技选择，使用普通攻击")
                    result = self.player_turn("attack")
            else:
                print("❌ 无效选择，使用普通攻击")
                result = self.player_turn("attack")
            
            self.battle_log.append(result["message"])
            print(f"\n✨ {result['message']}")
            
            if not self.boss.is_alive():
                print("\n" + "🎉"*25)
                print("     胜利！彼岸双生已被击败！")
                print("🎉"*25)
                return True
            
            time.sleep(1)
            print("\n👹 Boss回合...")
            time.sleep(0.5)
            boss_result = self.boss_turn()
            self.battle_log.append(boss_result["message"])
            print(f"💀 {boss_result['message']}")
            
            if not self.player.is_alive():
                print("\n" + "💔"*25)
                print("     战斗失败...")
                print("💔"*25)
                return False
            
            time.sleep(1)
        return False

# ========== 元素选择系统 ==========
class ElementSelection:
    def __init__(self, is_admin: bool, username: str, save_system: SaveSystem):
        self.is_admin = is_admin
        self.username = username
        self.save_system = save_system
    
    def select(self, force: bool = False) -> Optional[str]:
        existing = self.save_system.get_element(self.username)
        if existing and not force:
            print(f"\n🎮 你已选择元素：【{existing}】")
            return existing
        elements = NORMAL_ELEMENTS + ([HIDDEN_ELEMENT] if self.is_admin else [])
        print("\n" + "="*40)
        print("        元素选择 · 觉醒仪式")
        print("="*40)
        for i, e in enumerate(elements, 1):
            print(f"  {i}. {e}")
        while True:
            try:
                idx = int(input("\n请输入编号: ").strip()) - 1
                if 0 <= idx < len(elements):
                    sel = elements[idx]
                    self.save_system.set_element(self.username, sel)
                    print(f"\n✨ 元素觉醒！你获得了【{sel}】之力！")
                    return sel
                else:
                    print("❌ 编号无效")
            except ValueError:
                print("❌ 请输入数字编号")

# ========== 伙伴系统 ==========
class AllySystem:
    def __init__(self, username: str, player_element: str, save_system: SaveSystem):
        self.username = username
        self.player_element = player_element
        self.save_system = save_system
    
    def recruit_ally(self):
        current = self.save_system.get_allies(self.username)
        print(f"\n当前伙伴: {', '.join(current) if current else '无'}")
        
        if len(current) >= 4:
            print("❌ 伙伴已满（最多4个）")
            return
        
        available = [e for e in NORMAL_ELEMENTS if e not in current and e != self.player_element]
        if not available:
            print("📖 当前没有可招募的伙伴")
            return
        
        candidates = random.sample(available, min(3, len(available)))
        print("\n今日可招募的伙伴：")
        for i, e in enumerate(candidates, 1):
            desc = ELEMENT_DESCRIPTIONS.get(e, "")
            print(f"  {i}. {e} - {desc[:20]}...")
        
        try:
            choice = input("\n请选择（0取消）: ").strip()
            if choice == "0":
                return
            idx = int(choice) - 1
            if 0 <= idx < len(candidates):
                selected = candidates[idx]
                success = self.save_system.add_ally(self.username, selected)
                if success:
                    new_allies = self.save_system.get_allies(self.username)
                    print(f"\n✅ 成功招募 【{selected}】 元素伙伴！")
                    print(f"   当前伙伴: {', '.join(new_allies)}")
                else:
                    print(f"\n❌ 招募失败，请重试")
            else:
                print("❌ 编号无效")
        except ValueError:
            print("❌ 请输入数字")

# ========== 游戏主控制器 ==========
class Game:
    def __init__(self):
        self.login_system = LoginSystem()
        self.save_system = SaveSystem()
        self.running = True
    
    def run(self):
        print("\n" + "🔥"*20)
        print("     元 素 觉 醒")
        print("🔥"*20)
        
        if not self.login_system.login():
            return
        
        username = self.login_system.current_user
        is_admin = self.login_system.is_admin
        
        chosen = ElementSelection(is_admin, username, self.save_system).select(force=True)
        if chosen is None:
            return
        
        ally_system = AllySystem(username, chosen, self.save_system)
        
        while self.running:
            allies = self.save_system.get_allies(username)
            
            print("\n" + "="*40)
            print(f"  玩家: {username} | 元素: {chosen}")
            if allies:
                print(f"  伙伴: {', '.join(allies)} ({len(allies)}/4)")
            else:
                print(f"  伙伴: 无")
            if is_admin:
                print(f"  权限: 管理员 ⭐")
            print("="*40)
            print("  1. 查看状态")
            print("  2. 查看组合技")
            print("  3. 招募伙伴")
            print("  4. 挑战Boss · 彼岸双生")
            if is_admin:
                print("  5. 重新选择元素")
            print("  0. 退出游戏")
            print("-"*40)
            
            cmd = input("请选择: ").strip()
            
            if cmd == "1":
                print(f"\n📜 状态面板")
                print(f"   玩家: {username}")
                print(f"   元素: {chosen}")
                print(f"   描述: {ELEMENT_DESCRIPTIONS.get(chosen, '')}")
                allies = self.save_system.get_allies(username)
                if allies:
                    print(f"   伙伴: {', '.join(allies)}")
                else:
                    print(f"   伙伴: 无")
            
            elif cmd == "2":
                allies = self.save_system.get_allies(username)
                combos = ComboSystem(chosen, allies).get_available_combos()
                if combos:
                    print("\n✨ 可用组合技：")
                    for i, c in enumerate(combos, 1):
                        print(f"\n  {i}. 【{c['name']}】 {c['elements']}")
                        print(f"     {c['description']}")
                        print(f"     伤害:{c['damage']} 效果:{c['effect']} MP:{c['mp_cost']}")
                else:
                    print("\n📖 当前没有可用的组合技")
                    print("   招募相生元素的伙伴可解锁组合技！")
                    boost = ELEMENT_BOOST.get(chosen, "")
                    if boost:
                        print(f"   推荐招募: {boost} (相生元素)")
            
            elif cmd == "3":
                ally_system.recruit_ally()
            
            elif cmd == "4":
                allies = self.save_system.get_allies(username)
                stats = PlayerCombatStats(chosen, allies)
                battle = BattleSystem(stats, chosen, allies)
                victory = battle.start_battle()
                if victory:
                    print("\n✨ 恭喜！你击败了彼岸双生！")
                else:
                    print("\n💔 战斗失败...提升实力后再来吧！")
            
            elif cmd == "5" and is_admin:
                new_chosen = ElementSelection(is_admin, username, self.save_system).select(force=True)
                if new_chosen:
                    chosen = new_chosen
            
            elif cmd == "0":
                print(f"\n👋 {username}，元素之力与你同在。再见！")
                self.running = False
            
            else:
                print("❌ 无效指令。")

if __name__ == "__main__":
    Game().run()
