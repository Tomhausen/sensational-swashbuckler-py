# vars
speed = 8
deceleration = 0.95
max_enemy_speed = -75
enemies_to_reset: List[Sprite] = []
# bh1.3
daggers_collected = 0
# /bh1.3

orange_images = [
    assets.image("orange low"),
    assets.image("orange mid"),
    assets.image("orange high")
    ]
orange_animations = [
    assets.animation("orange attack low"),
    assets.animation("orange attack mid"),
    assets.animation("orange attack high")
    ]
red_images = [
    assets.image("red low"), 
    assets.image("red mid"),
    assets.image("red high")
    ]
red_animations = [
    assets.animation("red attack low"),
    assets.animation("red attack mid"),
    assets.animation("red attack high")
    ]

# sprites
orange = sprites.create(assets.image("orange low"), SpriteKind.player)
sprites.set_data_number(orange, "stance", 0)
sprites.set_data_boolean(orange, "attacking", False)

# setup
tiles.set_current_tilemap(assets.tilemap("level"))
tiles.place_on_random_tile(orange, assets.tile("orange spawn"))
scene.camera_follow_sprite(orange)
# bh1.1
scene.set_background_color(9)
scene.set_background_image(assets.image("background"))
scroller.scroll_background_with_camera(scroller.CameraScrollMode.ONLY_HORIZONTAL)
# /bh1.1

def spawn_enemy():
    if len(sprites.all_of_kind(SpriteKind.enemy)) < 3:
        enemy = sprites.create(assets.image("red low"), SpriteKind.enemy)
        sprites.set_data_number(enemy, "stance", 0)
        enemy.set_position(orange.x + 110, orange.y)
game.on_update_interval(1500, spawn_enemy)

def end_reached(orange, location):
    game.over(True)
scene.on_overlap_tile(SpriteKind.player, assets.tile("end"), end_reached)

def heighten_stance():
    new_player_stance = sprites.read_data_number(orange, "stance") + 1
    if new_player_stance < 3:
        sprites.set_data_number(orange, "stance", new_player_stance)
        orange.set_image(orange_images[new_player_stance])
controller.up.on_event(ControllerButtonEvent.PRESSED, heighten_stance)

def lower_stance():
    new_player_stance = sprites.read_data_number(orange, "stance") - 1
    if new_player_stance > -1:
        sprites.set_data_number(orange, "stance", new_player_stance)
        orange.set_image(orange_images[new_player_stance])
controller.down.on_event(ControllerButtonEvent.PRESSED, lower_stance)

# gh1
def throw_dagger():
    dagger = sprites.create_projectile_from_sprite(image.create(16, 16), orange, 100, 0)
    dagger.left = orange.x
    orange.vx = -20
    animation.run_image_animation(dagger, assets.animation("throwing dagger"), 50, True)

def throttle_throw_dagger():
    # bh1.3
    global daggers_collected
    if daggers_collected > 0:
        timer.throttle("throw dagger", 2000, throw_dagger)
        daggers_collected -= 1
    # /bh1.3
    # timer.throttle("throw dagger", 2000, throw_dagger)
controller.B.on_event(ControllerButtonEvent.PRESSED, throttle_throw_dagger)

def overlap_dagger(duelist, dagger):
    if sprites.read_data_boolean(duelist, "attacking"):
        dagger.vx *= -1.25
    elif duelist.kind() == SpriteKind.enemy:
        duelist.destroy()
        dagger.destroy()
    else:
        game.over(False)
sprites.on_overlap(SpriteKind.enemy, SpriteKind.projectile, overlap_dagger)
sprites.on_overlap(SpriteKind.player, SpriteKind.projectile, overlap_dagger)

def dagger_hit_wall(dagger, location):
    dagger.destroy()
scene.on_hit_wall(SpriteKind.projectile, dagger_hit_wall)
# /gh1

# bh1.3
def drop_dagger(red: Sprite):
    if randint(1, 4) == 1:
        dagger_pickup = sprites.create(assets.image("dagger pickup"), SpriteKind.food)
        dagger_pickup.x = red.x
        dagger_pickup.bottom = red.bottom
# /bh1.3

def hit(orange, red):
    orange_stance = sprites.read_data_number(orange, "stance")
    red_stance = sprites.read_data_number(red, "stance")
    if orange_stance == red_stance:
        orange.vx -= 25
        red.vx += 25
        scene.camera_shake(2, 100)
    elif sprites.read_data_boolean(orange, "attacking"):
# bh1.3
        drop_dagger(red)
        red.destroy()
# /bh1.3
    else:
        game.over(False)
sprites.on_overlap(SpriteKind.player, SpriteKind.enemy, hit)

# bh1.3
def collect_dagger(orange, dagger):
    global daggers_collected
    daggers_collected += 1
    music.ba_ding.play()
    dagger.destroy()
sprites.on_overlap(SpriteKind.player, SpriteKind.food, collect_dagger)
# /bh1.3

def reset_player():
    stance = sprites.read_data_number(orange, "stance")
    orange.set_image(orange_images[stance])
    sprites.set_data_boolean(orange, "attacking", False)

def player_attack():
    sprites.set_data_boolean(orange, "attacking", True)
    stance = sprites.read_data_number(orange, "stance")
    animation.run_image_animation(orange, orange_animations[stance], 40, False)
    timer.after(400, reset_player)
        
def reset_enemy():
    if len(enemies_to_reset) < 1:
        return
    enemy = enemies_to_reset[0]
    enemies_to_reset.shift()
    stance = sprites.read_data_number(enemy, "stance")
    enemy.set_image(red_images[stance])
    sprites.set_data_boolean(enemy, "attacking", False)

def enemy_attack(enemy: Sprite):
    sprites.set_data_boolean(enemy, "attacking", True)
    stance = sprites.read_data_number(enemy, "stance")
    animation.run_image_animation(enemy, red_animations[stance], 40, False)
    enemies_to_reset.append(enemy)
    timer.after(400, reset_enemy)

def randomise_enemy_stance(enemy: Sprite):
    current_stance = sprites.read_data_number(enemy, "stance")
    if not current_stance == 1:
        current_stance = 1
    else:
        current_stance += randint(-1, 1)
    enemy.set_image(red_images[current_stance])
    sprites.set_data_number(enemy, "stance", current_stance)

def enemy_behaviour(enemy: Sprite):
    if not sprites.read_data_boolean(enemy, "stunned"):
        if enemy.vx > max_enemy_speed:
            enemy.vx -= 0.5
        if not sprites.read_data_boolean(enemy, "attacking"):
            if randint(1, 60) == 1:
                enemy_attack(enemy)
            if randint(1, 60) == 1 :
                randomise_enemy_stance(enemy)
    
def player_movement():
    if controller.right.is_pressed():
        orange.vx += speed
    elif controller.left.is_pressed():
        orange.vx -= speed
    orange.vx *= deceleration

# bh1.2
def dash_back():
    orange.vx = -200

def throttle_dash():
    timer.throttle("dash", 2000, dash_back)
controller.combos.attach_combo("ll", dash_back)
# /bh1.2

def player_behaviour():
    player_movement()
    if sprites.read_data_boolean(orange, "attacking"):
        return
    if controller.A.is_pressed():
        player_attack()

def tick():
    for enemy in sprites.all_of_kind(SpriteKind.enemy):
        enemy_behaviour(enemy)
    player_behaviour()  
game.on_update(tick)
