# Import necessary libraries
import pygame
import os
import sqlite3
from os import listdir
from os.path import isfile, join


#Initialize pygame modules
pygame.init()
pygame.font.init()


# Define colors and game constants
white = (255, 255, 255)
black = (0,0,0)


# Game settings and initial values
ScreenType = 0 # 0 = main menu, 1..4 = different game screens
SCREEN_WIDTH = 1400 # window width in pixels
SCREEN_HEIGHT = 800 # window height in pixels

TotalBullets = 5 # number of bullets in current clip / burst pool timer refill
main_shoot = True # controls player shoot availability tied to a delay timer
shoot = True # extra shoot flag present in code (not heavily used)
MaxAmmo = 30 # total ammo reserve displayed as "MaxAmmo"


jumping = False # is the player currently jumping
can_be_hurt = False # whether player can currently take damage
gravity = 1 # gravity applied to jumping
JumpHeight = 20# initial jump velocity magnitude
vel = 9 # base velocity for bullets and other movement uses
velocity = JumpHeight # current vertical velocity used by jump logic


# Enemy and player health values
Health = 100 # player health value
enemyHealth = 100
Enemy2Health = 100
Enemy3Health = 100
Enemy4Health = 100
Boss_Health = 300


# Timed events for gameplay mechanics
gain_bullet = pygame.USEREVENT + 1 # event to refill the clip
pygame.time.set_timer(gain_bullet, 3000) # gain bullets every 3 seconds

shoot_delay = pygame.USEREVENT + 2 # event to end shooting cooldown window
pygame.time.set_timer(shoot_delay, 500) # shoot cooldown 500 ms

damage_delay = pygame.USEREVENT + 3 # event to re-enable damage after delay
pygame.time.set_timer(damage_delay, 1000)  #damage invulnerability duration 1s


# Load background and UI images
background = pygame.image.load("assets/background/citybackground.png")#makes the backround image
MainMenu = pygame.image.load("assets/background/main_menu1.png")#makes the main screen image
deathscreen = pygame.image.load('assets/background/death.png')#makes the death screen
LeaderBoardBackground = pygame.image.load("assets/background/leaderboard.jpg")# makes te background image of the leaderboard


# Load sound effects and music
pygame.mixer.init()
MainSound = pygame.mixer.Sound("assets/sound/HomeScreenMusic.mp3")  
runningSound = pygame.mixer.Sound("assets/sound/running.wav")
GunShot = pygame.mixer.Sound("assets/sound/shot.mp3")
GunReload = pygame.mixer.Sound("assets/sound/reload.mp3")
pygame.mixer.music.load("assets/sound/LevelMusic.MP3")
# background music playback settings
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(loops = -1)


# Load font
font = pygame.font.Font('assets/font/Retro.ttf',50)


# Function to render text on screen
def Text(MaxAmmo, Colour,X, Y):
    Text = font.render(MaxAmmo, True, Colour)
    screen.blit(Text,[X,Y])


# Flip sprite images horizontally
def flip(sprites):
    return[pygame.transform.flip(sprite, True, False) for sprite in sprites]


# Load sprite sheet and extract individual frames
def load_Sprite(dir1,  file, w,h, direction = False):
    path = join ('assets/',dir1, file)
    sprite_sheet = pygame.image.load(path).convert_alpha()

    all_sprites = {}

    sprites = []
    for i in range(sprite_sheet.get_width() // w):
        surface = pygame.Surface((w, h), pygame.SRCALPHA, 32)
        rect = pygame.Rect(i * w, 0, w, h)
        surface.blit(sprite_sheet, (0, 0), rect)
        sprites.append(pygame.transform.scale2x(surface))


            
    return sprites


#load block images for floor tiles
def get_block():
    path = join('assets/floor','flooring 2.png')
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((48, 48),pygame.SRCALPHA, 32)
    rect = pygame.Rect(550, 41, 48, 48)
    surface.blit(image,(00, 00),rect)
    return (surface)


# Bullet class for player and enemy projectiles
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, flip):
        super().__init__()
        #pygame.mixer.music.unload()

        path = join('assets/ammo','Bullet.png')
        self.image = pygame.image.load(path).convert_alpha()

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.flip = flip
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self): # move the bullet each frame according to flip and global vel
        if self.flip == False:
            self.rect.x += vel

        if self.flip == True:
            self.rect.x -= vel                
            self.image = pygame.transform.flip(self.image, True, False)
            #print("yes")


   # def kill(self):
       # BulletGroup.remove(self)


# Base object class for drawable game object
class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name = None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


# Block class for floor tiles
class Block(Object):
    def __init__(self, x, y):
        super().__init__(x, y, 48, 48)
        self.block = get_block()
        self.image.blit(self.block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)
    def draws(self):
        self.image.blit(self.block, (self.x, self.y))




# TextBox class for leaderboard display
class TextBox():
    def __init__(self, x,y,w, h, x2,y2 , text, Font):
        self.colour = black
        self.box = pygame.Rect(0,0, w, h)
        self.box.center = (x, y)

        self.text  =str(text)
        self.render_text = Font.render(self.text, True, white)
        self.rect = self.render_text.get_rect(center =(x,y))
        self.colour2 = white

    def draw(self):
        pygame.draw.rect(screen, self.colour, self.box)
        screen.blit(self.render_text, self.rect)



# Spike trap class
class spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/traps/spike.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

        
    def draws(self):
        screen.blit(self.image, self.rect)


# Roof spike trap class
class RoofSpike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('assets/traps/RoofSpike.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
        
    def draws(self):
        screen.blit(self.image, self.rect)
    

# Main player character class  
class Main(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.x = x
        self.y = y
        self.current_frame = 0
        self.sprite = image
        self.image = self.sprite[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_speed = 0.2
        self.animation_counter = 0
        self.shoot_cooldown = 150
        self.last_shot_time = pygame.time.get_ticks()
        self.last_hit_time = pygame.time.get_ticks()

        self.stop = True  # whether player is not moving

        self.flip = False  # facing direction indicator

    # Move character and set direction    
    def move(self, vx, vy):
        self.rect.x += vx
        self.rect.y += vy
        self.stop = False 
        if vx < 0:
            self.flip = True

        if vx > 0:
            self.flip = False

    # Animate character based on state
    def animate(self, image1, image2, image3):
        #image1 is idle
        #image2 is moving
        #image3 is jumping
        if self.stop == True:
            self.sprite = image1
            

        elif self.x > 0:
            self.sprite = image2
           

        if jumping == True:
            self.sprite = image3
           

        
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            # advance animation frame when counter reaches threshold
            self.animation_counter = 0
            self.current_frame += 1
            if self.current_frame >= len(self.sprite):
                self.current_frame = 0
            self.image = self.sprite[self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)

            if self.flip == True: # flip the current frame when facing left
                
                self.image = pygame.transform.flip(self.image, True, False)

    def pots(self, key):
        # set stop flag when no left/right/up keys pressed
        if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT] and not key[pygame.K_UP]:
            self.stop = True

    def can_shoot_player(self):
        now = pygame.time.get_ticks()# get the tick since the game started
        
        if now - self.last_shot_time >= self.shoot_cooldown:
            #now - self.last_shot_time is the milisecond time since it last shot
            
            self.last_shot_time = now# update the last time it shot
            
            return True#lets the bullet being create
        return False#if not true then no bullet made 

    def can_damage(self):
        now = pygame.time.get_ticks()# get the tick since the game started
        
        if now - self.last_hit_time >= self.shoot_cooldown:
            #now - self.last_shot_time is the milisecond time since it last shot
            
            self.last_hit_time = now# update the last time it shot
            
            return True#lets the bullet being create
        return False#if not true then no bullet made 
                
class enemys(pygame.sprite.Sprite):
    # basic enemy with animation and shooting cooldown
    def __init__(self, x, y, image,direction):
        super().__init__()
        self.x = x
        self.y = y
        self.current_frame = 0
        self.sprite = image
        self.image = self.sprite[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_speed = 0.2
        self.animation_counter = 0
        
        self.shoot_cooldown1 = 2000# delay in milisecond of each bullet
        self.last_shot_time = pygame.time.get_ticks()#shoot at the start 
        
        if direction == 'left':
            self.flip = True
        if direction == 'right':
            self.flip = False

    def animate(self):
        # animate enemy by advancing frames after a larger counter threshold


        self.animation_counter += self.animation_speed
        if self.animation_counter >= 7:
            self.animation_counter = 0
            self.current_frame += 1
            if self.current_frame >= len(self.sprite):
                self.current_frame = 0
            self.image = self.sprite[self.current_frame]
            self.mask = pygame.mask.from_surface(self.image)
        
    
    def can_shoot1(self):
        now = pygame.time.get_ticks()# get the tick since the game started
        
        if now - self.last_shot_time >= self.shoot_cooldown1:
            #now - self.last_shot_time is the milisecond time since it last shot
            
            self.last_shot_time = now# update the last time it shot
            
            return True#lets the bullet being create
        return False#if not true then no bullet made
    

#final boss class
class finalboss:
    def __init__(self,x, y, image):
        self.x = x
        self.y = y
        self.current_frame = 0
        self.sprite = image
        self.image = self.sprite
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_speed = 0.2
        self.animation_counter = 0
        
        self.shoot_cooldown1 = 2000# delay in milisecond of each bullet
        self.last_shot_time = pygame.time.get_ticks()#shoot at the start 

    def can_shoot1(self):
        now1 = pygame.time.get_ticks()# get the tick since the game started
        
        if now1 - self.last_shot_time >= self.shoot_cooldown1:
            #now - self.last_shot_time is the milisecond time since it last shot
            
            self.last_shot_time = now1# update the last time it shot
            
            return True#lets the bullet being create
        return False#if not true then no bullet made
        

    
    

#~~~~~ Pygame initialization and groups ~~~~~
pygame.init
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


# load player sprites for different states (idle, run, jump)
mainChrIdle = load_Sprite('player', 'Gunner_Yellow_Idle.png', 48, 48 )
mainChrRun = load_Sprite('player', 'Gunner_Yellow_Run.png', 48, 48 )
mainChrJump = load_Sprite('player','Gunner_Yellow_Jump.png', 48, 48)


main = Main( 25, 580, mainChrIdle)  # create player instance

bob = pygame.sprite.Group()
bob.add(main)  # group containing the player for collision checks

# groups for bullets
BulletGroup = pygame.sprite.Group()
EnemyBulletGroup = pygame.sprite.Group()
FinalBossBulletGroup= pygame.sprite.Group()




basicbaddie = load_Sprite('enemies','enemy1(2).png', 28, 47) # enemy animation frames


##badguysshoot = enemys(400,560,basicbaddieshoot)
badguys = enemys(400,560,basicbaddie, 'left')  #instantiate enemies
badguys1 = enemys(800,560,basicbaddie, 'left')
Jon = pygame.sprite.Group()
Jon.add(badguys)
Jon.add(badguys1)

Jon.add(enemys(1200,560,basicbaddie,'left'))

Boss = pygame.image.load('assets/enemies/BossEnemyAttackSingle.png' )

FinalBoss = finalboss(1200,460,Boss)
FinalBossGroup = pygame.sprite.Group()
FinalBossGroup.add_internal(FinalBoss) # custom group usage

# gameplay flags
hit = False
checkpoint = False

# floor and block group creation
blockGroup = pygame.sprite.Group()
floor = [Block(i * 48, SCREEN_HEIGHT - 48) for i in range (- SCREEN_WIDTH // 48, SCREEN_WIDTH * 2 // 48)]
for i in range(0,180):
    blocks = Block(46 * i,  SCREEN_HEIGHT - 48 * 4)
    blockGroup.add(blocks)



Objects = [ *floor, ] # list of floor objects (flattened)

time = pygame.time.get_ticks() # start time reference for level timers


# -------- Main game loop --------
run = True
while run:



    #capture keyboard state each frame
    key = pygame.key.get_pressed()

    # left/right movement and running sound playback
    if key[pygame.K_LEFT] == True:
        #print("left key is pressed")
        main.move(-5, 0)# move player left
        runningSound.play()# sound of running happens
    elif key[pygame.K_RIGHT] == True:
        #print("right key is pressed")
        main.move(5, 0) # move player right
        runningSound.play() # sound of running happens
    
    #up movement
    elif key[pygame.K_UP] == True:
        jumping = True
        #print("up key is pressed")
    if jumping:
        # apply jump vertical motion and gravity
        main.rect.y -= velocity
        velocity -= gravity
        if velocity < - JumpHeight:
            jumping = False
            velocity = JumpHeight
        
        

    # player shoot input, checks cooldown and clip count
    if key[pygame.K_SPACE] == True and main.can_shoot_player() and TotalBullets >0:
        TotalBullets -= 1
        #print("space key is pressed")
        MaxAmmo -= 1
        main_shoot = False
        bullet = Bullet(main.rect.x+52, main.rect.y+ 40, main.flip)
        BulletGroup.add(bullet)
        GunShot.play()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False  # handle window close

        # refill clip if timer fired and clip was not full    
        if event.type == gain_bullet and TotalBullets < 5:
            GunReload.play()
            TotalBullets = 5

        # when out of reserve ammo, set TotalBullets to -1 (prevents reload)    
        if MaxAmmo == 0:
            TotalBullets = -1
        # shoot_delay event re-enables main_shoot flag
        if event.type == shoot_delay:
            main_shoot = True
            
        # damage_delay event re-enables being hurt
        if event.type == damage_delay:
            can_be_hurt = True
            #print(can_be_hurt)
    
    # when checkpoint True player finished game, save to DB 
    if checkpoint == True:
        pygame.quit()
        con = sqlite3.connect("game.db")
        cursorObj = con.cursor()
        Username = input('Enter Username')
        Time = input('Your time was' + str(dt3))
        LeaderBoardTime = dt3
        entities = (Username, LeaderBoardTime)
        cursorObj.execute('INSERT INTO leaderboard(Username, TimeVal) VALUES (?,?)', entities)
        con.commit()

    # repeated damage_delay handling
    if event.type == damage_delay:
        can_be_hurt = True
        #print(can_be_hurt)

    # bullet for enemy
    for eachenemy in Jon:# loop through all enemys
        if eachenemy.can_shoot1():# if it been long enough time since last shot
            bullets = Bullet(eachenemy.rect.x+40, eachenemy.rect.y+40, eachenemy.flip)#create bullet
            EnemyBulletGroup.add(bullets)
            

        hit = pygame.sprite.spritecollide( eachenemy, bob, False)# enemy hit player
        for bullet in EnemyBulletGroup:
            hitplayerbullet = pygame.sprite.collide_mask(bullet, main)# enemy hit player
            if hitplayerbullet:
                if can_be_hurt:
                    Health -=25
                    print(Health)# dmg to player when shot
                    can_be_hurt = False
                    bullet.kill()

    # final boss group shooting logic
    for eachBoss in FinalBossGroup:
        if eachBoss.can_shoot1():
            bullets = Bullet(eachenemy.rect.x+40, eachenemy.rect.y+40, eachenemy.flip)#create bullet
            FinalBossBulletGroup.add(bullets)
            

        hit1 = pygame.sprite.spritecollide( eachBoss, bob, False)# enemy hit player
        for bullet in FinalBossBulletGroup:
            hitplayerbullet = pygame.sprite.collide_mask(bullet, main)# enemy hit player
            if hitplayerbullet:
                if can_be_hurt: 
                    Health -=25
                    print(Health)# dmg to player when shot
                    can_be_hurt = False
                    bullet.kill()

    # player bullet collision with enemies
    for eachbullet in BulletGroup:
        bulletHit = pygame.sprite.spritecollide(eachbullet, Jon, True)
        

        for eachhit in bulletHit:
            BulletGroup.remove(eachbullet)# remove bullet


    # debug / testing key to restore health
    if key[pygame.K_h] == True:
        Health =100
        #print("h key pressed")

           
    # -------- Screen type: main menu --------        
    if ScreenType == 0:#menu
        screen.blit(MainMenu,(0,0))# draw background
        Text('The Second Amendment', white, 530, 470) 
        if key[pygame.K_RETURN] == True:
            #print("return key is pressed")
            time = pygame.time.get_ticks()
            ScreenType = ScreenType + 1
        
        if key[pygame.K_l] == True:
            ScreenType = 4
            #print("l key is pressed")

        
    # -------- Screen type: level 1 gameplay --------
    if ScreenType == 1:#1stlevel
        screen.blit(background,(0,0))# draw background
        time2 = pygame.time.get_ticks()
        dt = (time2 - time)/1000 # time elapsed in seconds for the level

        if key[pygame.K_q] == True:
            ScreenType = 0
            #print("q key is pressed")
        if main.rect.x > 1400:
            main.rect.x = 0
            ScreenType = ScreenType + 1


            # update and cull bullets when advancing screens
            for bullet in BulletGroup:
                bullet.update()
                if bullet.rect.x<0:
                    bullet.kill()
                if bullet.rect.x > 1400:
                    bullet.kill()
            main.pots(key)

        BulletGroup.draw(screen)
        BulletGroup.update()

   
        EnemyBulletGroup.draw(screen)
        EnemyBulletGroup.update()

        BulletGroup.draw(screen)
        bob.draw(screen)# draws character
        Jon.draw(screen)
        
        blockGroup.draw(screen)

        main.animate(mainChrIdle,mainChrRun,mainChrJump)
        for enemy in Jon:
            enemy.animate()
        
        
        Text('Ammo',white, 10,40)
        Text(str(MaxAmmo),white, 130,40)
        Text('Time' + str(dt), white, 1150, 40)
        Text('Health ' + str(Health), white, 600, 40)

        
    # -------- Screen type: level 2 gameplay with spikes --------
    if ScreenType == 2:
        screen.blit(background,(0,0))# draw background
        if key[pygame.K_q] == True:
            ScreenType = 0
        if main.rect.x > 1400:
            main.rect.x = 00
            ScreenType = ScreenType + 1
        
            
         
        time3 = pygame.time.get_ticks()
        dt2 = (time3 - time)/1000
            

        BulletGroup.draw(screen)
        bob.draw(screen)# draws character


        # create several roof spike instances for this screen
        RoofSpikes1 = RoofSpike(300, 350)
        RoofSpikes2 = RoofSpike(500, 350)
        RoofSpikes3 = RoofSpike(700, 350)
        RoofSpikes4 = RoofSpike(900, 350)
        RoofSpikes5 = RoofSpike(1100, 350)
        RoofSpikeGroup = pygame.sprite.Group()
        RoofSpikeGroup.add(RoofSpikes1)
        RoofSpikeGroup.add(RoofSpikes2)
        RoofSpikeGroup.add(RoofSpikes3)
        RoofSpikeGroup.add(RoofSpikes4)
        RoofSpikeGroup.add(RoofSpikes5)


        # if player collides with any roof spike, set health to 0 (instant death)
        if pygame.sprite.collide_mask(RoofSpikes1,main) or pygame.sprite.collide_mask(RoofSpikes2,main) or pygame.sprite.collide_mask(RoofSpikes3,main) or pygame.sprite.collide_mask(RoofSpikes4,main) or pygame.sprite.collide_mask(RoofSpikes5,main):
            Health = 0 


        # create ground spikes
        spikes1 = spike(235,588)
        Spikes2 = spike(400, 588)
        Spikes3 = spike(600, 588)
        Spikes4 = spike(800, 588)
        Spikes5 = spike(1000, 588)
        Spikes6 = spike(1200, 588)
        SpikeGroup = pygame.sprite.Group()  
        SpikeGroup.add(spikes1)
        SpikeGroup.add(Spikes2)
        SpikeGroup.add(Spikes3)
        SpikeGroup.add(Spikes4)
        SpikeGroup.add(Spikes5)
        SpikeGroup.add(Spikes6) 
  

        # if player collides with any ground spike, set health to 0 (instant death)
        if pygame.sprite.collide_mask(spikes1,main) or pygame.sprite.collide_mask(Spikes2,main) or pygame.sprite.collide_mask(Spikes3,main) or pygame.sprite.collide_mask(Spikes4,main) or pygame.sprite.collide_mask(Spikes5,main) or pygame.sprite.collide_mask(Spikes6,main):
            Health = 0 

        blockGroup.draw(screen)

        
        main.animate(mainChrIdle,mainChrRun,mainChrJump)

        SpikeGroup.draw(screen)
        RoofSpikeGroup.draw(screen)
        
        Text('Ammo',white, 10,40)
        Text(str(MaxAmmo),white, 130,40)
        Text('Time' + str(dt2), white, 1150, 40)
        Text('Health ' + str(Health), white, 600, 40)


    # -------- Screen type: boss fight --------
    if ScreenType == 3:
        screen.blit(background,(0,0))# draw background
        time4 = pygame.time.get_ticks()
        dt3 = (time4 - time)/1000


        BulletGroup.draw(screen)
        BulletGroup.update()
        BulletGroup.draw(screen)
        bob.draw(screen)# draws character
        main.animate(mainChrIdle,mainChrRun,mainChrJump)


        # check player bullets reaching boss area and reduce boss health
        for bullets in BulletGroup:
            if bullets.rect.x > 1200:
                Boss_Health -= 25
                BulletGroup.remove(bullets)
        if Boss_Health > 0:
            screen.blit(Boss, (1200, 460))
            FinalBossBulletGroup.draw(screen)
            FinalBossBulletGroup.update()
        if Boss_Health <= 0:
            FinalBossBulletGroup.remove(bullet)          
        
        

        blockGroup.draw(screen)
        Text('Ammo',white, 10,40)
        Text(str(MaxAmmo),white, 130,40)
        Text('Time' + str(dt3), white, 1150, 40)
        Text('Health ' + str(Health), white, 600, 40)

        if main.rect.x > 1400:
            checkpoint = True # if the player finishes game it =True


    # -------- Screen type: leaderboard display (screen 4) --------
    if ScreenType == 4:
        screen.blit(LeaderBoardBackground,(0,0))    
        con = sqlite3.connect("game.db")
        cursorObj = con.cursor()
        strSQL = " SELECT * FROM leaderboard ORDER BY TimeVal ASC LIMIT 10"
        cursorObj.execute(strSQL)
        

        rows = cursorObj.fetchall()
        leaderboard = []
        i = 1
        for row in rows:
            # build a TextBox for each leaderboard row, using DB columns
            text = str(i) + "." + str(row[1])+ " " + str(row[2])
            item = TextBox((SCREEN_WIDTH //2),57*i, 300, 0, (SCREEN_WIDTH//2),57*i, str(text),font)

            i+=1
            leaderboard.append(item)

        

        if key[pygame.K_q]:
            #print("q key is pressed")
            ScreenType = 0

        for position in leaderboard:
            position.draw()   


    # -------- Global health and death handling --------
    if Health <= 0:
        Health = 0
    if Health == 0:
        screen.blit(deathscreen,(0,0))
        print(dt)
        pygame.quit

        

    pygame.display.update()
    clock.tick(60)


pygame.quit()
