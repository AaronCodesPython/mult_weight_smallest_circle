import pygame
import random
import math
NUM_POINTS = 100
NUM_POINTS_SELECT = 11
WIDTH = 512
HEIGHT = 512
BORDER_LIMIT_X = 50
BORDER_LIMIT_Y = 100


class Point:
    x = 0
    y = 0
    mult = 1
    def __init__(self,x,y,mult):
        self.x =x
        self.y = y
        self.mult = mult 

    def __eq__(self, other):
        return (
            isinstance(other, Point)
            and self.x == other.x
            and self.y == other.y
            and self.mult == other.mult
        )

    def __hash__(self):
        return hash((self.x, self.y, self.mult))
# pygame setup
pygame.init()
font = pygame.font.SysFont("Arial", 8)
font2 = pygame.font.SysFont("Arial", 38)
font3 = pygame.font.SysFont("Arial", 12)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

running = True
dt = 0


points = []
for x in range(NUM_POINTS):
    p = Point(random.randrange(BORDER_LIMIT_X, WIDTH - BORDER_LIMIT_X),
    random.randrange(BORDER_LIMIT_Y, HEIGHT - BORDER_LIMIT_Y), 1)
    points.append(p)

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

def get_Q(points):
    overall_sum = 0
    selected = []
    for p in points:
        overall_sum += p.mult
    for i in range(11):
        rand = random.randrange(0,overall_sum)
        cur_sum = 0
        
        for i in range(0,len(points)):
            cur_sum+= points[i].mult
            if(cur_sum >= rand):
                selected.append(points[i])
                break
    return selected

def dist(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def triangle_area(a, b, c):
    s = (a + b + c) / 2
    return math.sqrt(s * (s - a) * (s - b) * (s - c))

def smallest_enclosing_circle_radius(A, B, C):
    a = dist(B, C)
    b = dist(A, C)
    c = dist(A, B)
    
    # Use cosine law to check for obtuse/right triangle
    def is_obtuse(x, y, z):  # checks if angle opposite side x is ≥ 90°
        return x**2 >= y**2 + z**2

    if is_obtuse(a, b, c) or is_obtuse(b, a, c) or is_obtuse(c, a, b):
        return max(a, b, c) / 2  # diameter of enclosing circle

    area = triangle_area(a, b, c)
    return (a * b * c) / (4 * area)

def is_in_circle(r, origin, p, epsilon=1e-6):
    return dist(origin, p) <= r + epsilon

def midpoint(P, Q):
    return pygame.Vector2((P.x + Q.x)/2, (P.y + Q.y)/2)
def circumcenter(A, B, C):
    x1, y1 = A.x, A.y
    x2, y2 = B.x, B.y
    x3, y3 = C.x, C.y

    d = 2*(x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))
    ux = ((x1*x1 + y1*y1)*(y2 - y3)
        + (x2*x2 + y2*y2)*(y3 - y1)
        + (x3*x3 + y3*y3)*(y1 - y2)) / d
    uy = ((x1*x1 + y1*y1)*(x3 - x2)
        + (x2*x2 + y2*y2)*(x1 - x3)
        + (x3*x3 + y3*y3)*(x2 - x1)) / d
    return pygame.Vector2(ux, uy)

def get_circle(sel):
    # 1) find the maximizing triplet and its radius
    max_rad = -1
    best_triplet = None
    for i in range(len(sel)):
        for j in range(i+1, len(sel)):
            for k in range(j+1, len(sel)):
                r = smallest_enclosing_circle_radius(sel[i], sel[j], sel[k])
                if r > max_rad:
                    max_rad, best_triplet = r, (sel[i], sel[j], sel[k])

    A, B, C = best_triplet
    # 2) figure out if the triangle is obtuse
    a = dist(B, C); b = dist(A, C); c = dist(A, B)
    is_obtuse = (
        a*a >= b*b + c*c
        or b*b >= a*a + c*c
        or c*c >= a*a + b*b
    )

    # 3 compute the exact center
    if is_obtuse:
        # longest side
        if a >= b and a >= c:
            center = midpoint(B, C)
        elif b >= a and b >= c:
            center = midpoint(A, C)
        else:
            center = midpoint(A, B)
    else:
        center = circumcenter(A, B, C)

    return center, best_triplet, max_rad

    #return maxPointSet
BUF = 8
CUR = 0
sel = []
origin = Point(0,0,1)
max_rad = 0
done = False
k = 0
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")
    for c in points:
        pygame.draw.circle(screen, "black", pygame.Vector2(c.x,c.y), 8)
        text = font.render(str(c.mult), True, "white")
        text_rect = text.get_rect(center=(c.x, c.y))
        screen.blit(text, text_rect)

    keys = pygame.key.get_pressed()

    
    if keys[pygame.K_r]:   
        for x in range(NUM_POINTS):
            p = Point(random.randrange(BORDER_LIMIT_X, WIDTH - BORDER_LIMIT_X),
            random.randrange(BORDER_LIMIT_Y, HEIGHT - BORDER_LIMIT_Y), 1)
            points[x] = p
            
        sel = []
        done = False
        k = 0
        origin = Point(0,0,1)
        max_rad = 0
    if keys[pygame.K_t]:
        CUR = CUR + 1
        if(CUR %  BUF == 0 and not done):
            CUR = 0
            k+=1
            sel = get_Q(points)
            origin,max_rad_set,max_rad = get_circle(sel)
            outliers = 0
            for p in points:
                if not is_in_circle(max_rad,origin,p):
                    outliers+=1
                    p.mult *=2
            if(outliers == 0):
                done = True

    for p in sel:
        if p in max_rad_set:
            pygame.draw.circle(screen, "blue", pygame.Vector2(p.x,p.y), 12)
        else:
            pygame.draw.circle(screen, "red", pygame.Vector2(p.x,p.y), 12)
    pygame.draw.circle(screen, "black", (origin.x,origin.y), max_rad, 3)
    #print("orig:"+str(origin.x)+" "+str(origin.y))

    text3 = font3.render("r:"+str(max_rad)+"   k:"+str(k), True, "black")
    text_rect3 = text3.get_rect()
    text_rect3.bottomright = (WIDTH - 10, HEIGHT - 10)  

    screen.blit(text3,text_rect3)
    if done:
        text2 = font2.render("Done!", True, "black")
        text_rect2 = text.get_rect(center=(WIDTH/2, HEIGHT-60))
        screen.blit(text2, text_rect2)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(20) / 1000

pygame.quit()


