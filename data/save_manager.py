import json
import os

class SaveManager:
    def __init__(self, mode="single_player"):
        self.mode = mode  # 模式可以是 "single_player" 或 "multiplayer"
        self.save_folder = "saves"
        self.max_saves = 6  # 最多保存6个存档
        self.save_files = [f"{self.mode}_save_{i}.json" for i in range(1, self.max_saves + 1)]

        # 创建存档文件夹（如果不存在）
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

    def get_save_path(self, save_slot):
        """根据存档槽获取存档路径"""
        return os.path.join(self.save_folder, self.save_files[save_slot - 1])

    def save_game(self, player, save_slot):
        """保存当前游戏进度到指定存档槽"""
        save_data = {
            "player_x": player.rect.x,
            "player_y": player.rect.y,
            "player_dead": player.dead,
            "player_score": player.total_score,
            "player_state": player.state,
            "current_level": player.current_level,
        }
        save_path = self.get_save_path(save_slot)
        with open(save_path, 'w') as file:
            json.dump(save_data, file)
            print(f"游戏已保存到 {save_path}")

    def load_game(self, player, save_slot):
        """从指定存档槽加载游戏进度"""
        save_path = self.get_save_path(save_slot)
        if os.path.exists(save_path):
            with open(save_path, 'r') as file:
                save_data = json.load(file)
                player.rect.x = save_data["player_x"]
                player.rect.y = save_data["player_y"]
                player.life = save_data["player_life"]
                player.score = save_data["player_score"]
                player.state = save_data["player_state"]
                player.current_level = save_data["current_level"]
                print(f"游戏进度已加载自 {save_path}")
        else:
            print(f"存档 {save_slot} 不存在。")

    def delete_save(self, save_slot):
        """删除指定存档槽的存档"""
        save_path = self.get_save_path(save_slot)
        if os.path.exists(save_path):
            os.remove(save_path)
            print(f"存档 {save_slot} 已删除。")
        else:
            print(f"存档 {save_slot} 不存在。")
