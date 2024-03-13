//  vars
let speed = 8
let deceleration = 0.95
let max_enemy_speed = -75
let enemies_to_reset : Sprite[] = []
let orange_images = [assets.image`orange low`, assets.image`orange mid`, assets.image`orange high`]
let orange_animations = [assets.animation`orange attack low`, assets.animation`orange attack mid`, assets.animation`orange attack high`]
let red_images = [assets.image`red low`, assets.image`red mid`, assets.image`red high`]
let red_animations = [assets.animation`red attack low`, assets.animation`red attack mid`, assets.animation`red attack high`]
//  sprites
let orange = sprites.create(assets.image`orange low`, SpriteKind.Player)
sprites.setDataNumber(orange, "stance", 0)
sprites.setDataBoolean(orange, "attacking", false)
//  setup
tiles.setCurrentTilemap(assets.tilemap`level`)
tiles.placeOnRandomTile(orange, assets.tile`orange spawn`)
scene.cameraFollowSprite(orange)
scene.setBackgroundColor(9)
game.onUpdateInterval(1500, function spawn_enemy() {
    let enemy: Sprite;
    if (sprites.allOfKind(SpriteKind.Enemy).length < 3) {
        enemy = sprites.create(assets.image`red low`, SpriteKind.Enemy)
        sprites.setDataNumber(enemy, "stance", 0)
        enemy.setPosition(orange.x + 110, orange.y)
    }
    
})
scene.onOverlapTile(SpriteKind.Player, assets.tile`end`, function end_reached(orange: Sprite, location: tiles.Location) {
    game.over(true)
})
controller.up.onEvent(ControllerButtonEvent.Pressed, function heighten_stance() {
    let new_player_stance = sprites.readDataNumber(orange, "stance") + 1
    if (new_player_stance < 3) {
        sprites.setDataNumber(orange, "stance", new_player_stance)
        orange.setImage(orange_images[new_player_stance])
    }
    
})
controller.down.onEvent(ControllerButtonEvent.Pressed, function lower_stance() {
    let new_player_stance = sprites.readDataNumber(orange, "stance") - 1
    if (new_player_stance > -1) {
        sprites.setDataNumber(orange, "stance", new_player_stance)
        orange.setImage(orange_images[new_player_stance])
    }
    
})
sprites.onOverlap(SpriteKind.Player, SpriteKind.Enemy, function hit(orange: Sprite, red: Sprite) {
    let orange_stance = sprites.readDataNumber(orange, "stance")
    let red_stance = sprites.readDataNumber(red, "stance")
    if (orange_stance == red_stance) {
        orange.vx -= 25
        red.vx += 25
        scene.cameraShake(2, 100)
    } else if (sprites.readDataBoolean(orange, "attacking")) {
        red.destroy()
    } else {
        game.over(false)
    }
    
})
function player_attack() {
    sprites.setDataBoolean(orange, "attacking", true)
    let stance = sprites.readDataNumber(orange, "stance")
    animation.runImageAnimation(orange, orange_animations[stance], 40, false)
    timer.after(400, function reset_player() {
        let stance = sprites.readDataNumber(orange, "stance")
        orange.setImage(orange_images[stance])
        sprites.setDataBoolean(orange, "attacking", false)
    })
}

function enemy_attack(enemy: Sprite) {
    sprites.setDataBoolean(enemy, "attacking", true)
    let stance = sprites.readDataNumber(enemy, "stance")
    animation.runImageAnimation(enemy, red_animations[stance], 40, false)
    enemies_to_reset.push(enemy)
    timer.after(400, function reset_enemy() {
        if (enemies_to_reset.length < 1) {
            return
        }
        
        let enemy = enemies_to_reset[0]
        enemies_to_reset.shift()
        let stance = sprites.readDataNumber(enemy, "stance")
        enemy.setImage(red_images[stance])
        sprites.setDataBoolean(enemy, "attacking", false)
    })
}

function randomise_enemy_stance(enemy: Sprite) {
    let current_stance = sprites.readDataNumber(enemy, "stance")
    if (!(current_stance == 1)) {
        current_stance = 1
    } else {
        current_stance += randint(-1, 1)
    }
    
    enemy.setImage(red_images[current_stance])
    sprites.setDataNumber(enemy, "stance", current_stance)
}

function enemy_behaviour(enemy: Sprite) {
    if (!sprites.readDataBoolean(enemy, "stunned")) {
        if (enemy.vx > max_enemy_speed) {
            enemy.vx -= 0.5
        }
        
        if (!sprites.readDataBoolean(enemy, "attacking")) {
            if (randint(1, 60) == 1) {
                enemy_attack(enemy)
            }
            
            if (randint(1, 60) == 1) {
                randomise_enemy_stance(enemy)
            }
            
        }
        
    }
    
}

function player_movement() {
    if (controller.right.isPressed()) {
        orange.vx += speed
    } else if (controller.left.isPressed()) {
        orange.vx -= speed
    }
    
    orange.vx *= deceleration
}

controller.combos.attachCombo("ll", function dash_back() {
    orange.vx = -200
})
function player_behaviour() {
    player_movement()
    if (sprites.readDataBoolean(orange, "attacking")) {
        return
    }
    
    if (controller.A.isPressed()) {
        player_attack()
    }
    
}

game.onUpdate(function tick() {
    for (let enemy of sprites.allOfKind(SpriteKind.Enemy)) {
        enemy_behaviour(enemy)
    }
    player_behaviour()
})
