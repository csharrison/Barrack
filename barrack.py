#Charlie
#Jan 15, 2011
#Barrack
#you know, the awesome game

import pygame
from pygame.locals import *
from random import *

class Ball(object):
	def __init__(self,(x,y),r,vx,vy):
		#x and y are int locations, rx and ry are float locations
		self.x, self.y = self.rx, self.ry = (x,y)
		self.vx, self.vy = vx,vy#starting velocities
		self.r = r#radius
		self.bounced = False
		self.bbox = pygame.Rect(x-r,y-r,r*2+1,r*2+1)#the balls bounding box
		
	def update(self,screen, m,dim):
		self.draw(screen,(0,0,0))#erase where you were last
		to_update = (self.x-self.r,self.y-self.r,self.r*2,self.r*2)#update this later (avoids "blinking")
		
		self.rx += self.vx
		self.ry += self.vy
		self.x = int(self.rx)
		self.y = int(self.ry)
		
		self.bounce(screen, m,dim)
		self.bbox = pygame.Rect(self.x-self.r-3,self.y-self.r-3,self.r*2+6,self.r*2+6)
		#pygame.draw.rect(screen,(250,250,250),(self.bbox))
		#pygame.display.update()
		self.draw(screen,(0,200,250))

		pygame.display.update([to_update,self.bbox])#update the two positions

	def bouncex(self): self.vx*=-1#just used to shorten/neaten code
	def bouncey(self): self.vy*=-1
	
	def bounce(self,screen, m,dim):			
		upper = int(round(self.y - self.r))
		lower = int(round(self.y + self.r))
		lefter = int(round(self.x - self.r))
		righter = int(round(self.x + self.r))
		
		bouncedx, bouncedy = True,True
		
		if upper < 0: 
			self.ry = self.r
			self.bouncey()
		elif m[self.x][upper] == 1: 
			self.ry += 1
			self.bouncey()

		elif lower > dim[1]-1:
			self.ry = dim[1]-self.r
			self.bouncey()
			
		elif m[self.x][lower] == 1: 
			self.ry -= 1
			self.bouncey()
		else: bouncedy = False

		if righter > dim[0]-1:
			self.rx = dim[0] - self.r
			self.bouncex()
			
		elif m[righter][self.y] == 1: 
			self.rx -= 1
			self.bouncex()

		elif lefter < 0:
			self.rx = self.r
			self.bouncex()
			
		elif m[lefter][self.y] == 1: 
			self.rx += 1
			self.bouncex() 
		else: bouncedx = False
		
		self.bounced = (bouncedx or bouncedy)

	def draw(self,screen, color):
		pygame.draw.circle(screen, color,(self.x,self.y),self.r)
		
class Line(object):
	def __init__(self, (x,y), direction, size, color, speed=1):
		#direction: (0,1) or (1,0)
		self.line_list = [(x,y)]
		self.direction = direction
		self.speed = speed
		self.b_growing = True#growing from beginning
		self.e_growing = True#growing from the end
		self.bbox = pygame.Rect(x,y,3,3)#FIX BOUNDING BOX ERRORS
		self.dead = False
		self.color = color
	def grow(self, screen, m, dim):
		"extends the line in the direction it is going, will stop if it hits a wall"
		for i in xrange(self.speed):#do it twice if your line is twice as fast etc.
			bx,by = self.line_list[0]
			ex,ey = self.line_list[len(self.line_list)-1]

			#append a cell to the beginning of the line
			if self.b_growing == True:
				x = bx - self.direction[0]
				y = by - self.direction[1]
				self.bbox[:2] = [x,y]
				self.bbox[2] += self.direction[0]
				self.bbox[3] += self.direction[1]
				
				if (x<0 or y<0) or m[x][y] == 1: #hits a side or another line
					self.b_growing = False
				else:#keep growin
					self.line_list.insert(0,(x,y))
					bx,by = x,y
					m[bx][by] = 1
					pygame.draw.circle(screen,self.color,(bx,by),0)

					#append a cell to the end of the line
			if self.e_growing == True:
				x = ex + self.direction[0]
				y = ey + self.direction[1]
				self.bbox[2] += self.direction[0]
				self.bbox[3] += self.direction[1]

				if (x>=dim[0] or y>=dim[1]) or m[x][y] == 1: #hits a wall or another line
					self.e_growing = False
				else:#keep growin
					self.line_list.append((x,y))
					ex,ey = x,y
					m[ex][ey] = 1
					pygame.draw.circle(screen,self.color,(ex,ey),0)

			pygame.display.update([(bx,by,1,1),(ex,ey,1,1)])
		return m, (self.b_growing == True or self.e_growing == True)
		
	def delete(self, screen, m, b_color):#erase the line
		"erases the line completely, and stops it from growing further"
		for x,y in self.line_list:
			m[x][y] = 0
			pygame.draw.circle(screen,b_color,(x,y),0)
			pygame.display.update((x,y,1,1))
		self.e_growing = False
		self.b_growing = False
		self.dead = True
		return m


def draw_point(screen,x,y,color):
	pygame.draw.circle(screen,(150,50,100),(x,y),0)
	pygame.display.update((x,y,1,1))
	
def update_map(screen,(x,y,w,h),m, color):
	for i in xrange(x,x+w):
		for j in xrange(y,y+h):
			try:
				if m[i][j] == 1: pygame.draw.circle(screen,color,(i,j),0)
			except: pass
	pygame.display.update((x,y,w,h))

def fill_space(line,m, balls):
	"fills in all squares that have no balls in them"
	#this function gets called every time a line successfully gets stopped (hits a wall or another line) on the growing and beginning end 
	#a line can only break up a rectangle into 2 smaller rectangles, so 
	#if it's a horizontal line: scour the area ABOVE the line and BELOW the line for balls
	#if it's a vertical line: scour the area to the RIGHT and LEFT of the line for balls
	#if no balls are found, fill in the area (i.e. set the map squares to ON - this'll be important later for scoring)
	bx, by = line.line_list[0][::]#beginning points
	ex, ey = line.line_list[len(line.line_list)-1][::]#end points
	dir = line.direction #remember: (1,0) or (0,1) 
	
	if dir == (1,0):#i.e. a horizontal line
		#start at bx,by and go up and over (to ex) until you hit another ON tile
		y = by-1
		while m[bx][y] != 1 and (y>0 and y<len(m[0])-1):
		#keep going up till it hits something
			y-=1
		uprect = (bx,y,ex-bx+1,by-y+1)
		
		y = by + 1
		while m[bx][y] != 1 and (y>0 and y<len(m[0])-1):#keep going down till it hits something
			y+=1
		downrect = (bx,ey,(ex-bx)+1,(y-by)+1)
		return uprect,downrect
	elif dir == (0,1):
		x = bx-1
		while m[x][by] != 1 and (x>0 and x<len(m)-1):
		#keep going left till it hits something
			x-=1
		leftrect = (x,by,ex-x,ey-by+1)
		x = bx + 1
		while m[x][by] != 1 and (x>0 and x<len(m)-1):#keep going right till it hits something
			x+=1
		rightrect = (bx,by,(x-bx),(ey-by)+1)
		return leftrect,rightrect
		

def rect_collision(screen,rects,balls, color):
	filled_in = 0
	for rect in rects:
		r = pygame.Rect(rect)
		if r.collidelist(balls) == -1: 
			filled_in += (rect[2]*rect[3])
			pygame.draw.rect(screen,color,r)
			pygame.display.update((r))
	return filled_in
		

def update_fonts(screen,dim, l,p,lines,lives,percent,lines_num):
	s = l.render(str("Lives left: "+str(lives)), True,(250,0,0))
	s2 = p.render(str(percent)+"% Filled", True, (250,0,0))
	s3 = lines.render(str(lines_num)+" lines used",True,(250,0,0))
	
	pygame.draw.rect(screen,(50,50,50),(0,dim[1],dim[0],100))
	screen.blit(s,(10,dim[1]+5))
	screen.blit(s2,(10,dim[1]+35))
	screen.blit(s3,(10,dim[1]+65))
	pygame.display.update()

b_color = (0,0,0)
pygame.init()
#dim = (1366,668)
dim = (600,600)
screen = pygame.display.set_mode((dim[0],dim[1]+100))
pygame.draw.rect(screen,(100,100,100),(0,dim[1],dim[0],101))
pygame.draw.rect(screen,b_color,(0,0,dim[0],dim[1]))
clock = pygame.time.Clock()
lines = []
growing_lines = []
line_counter = 0
lives_num = 5
direction = (1,0)
balls = []
ballboxes = []
percent = 0
total_filled = 0

line_color = (120,20,40)

live_font = pygame.font.Font(None,40)
p_font = pygame.font.Font(None,40)
lines_used = pygame.font.Font(None,40)

update_fonts(screen,dim,live_font,p_font,lines_used,lives_num, percent,line_counter)

for i in xrange(8):
	b = Ball((randint(20,dim[0]-10),randint(20,dim[1]-10)),5,choice([-1,1])*uniform(0,1),choice([1,-1])*uniform(0,1))
	balls.append(b)
	ballboxes.append(b.bbox)
	
m = [[0 for i in xrange(dim[1])] for i in xrange(dim[0])]#damn we gots to use the map
					
pygame.display.update()

going = True
while going:
	clock.tick(300)
	for e in pygame.event.get():
		mx,my = [int(pygame.mouse.get_pos()[i]) for i in xrange(2)]
		if e.type == QUIT:
				going = False
		elif e.type == KEYDOWN:
			if e.key == K_ESCAPE: going = False
			elif e.key == K_SPACE: direction = (0,1)
		elif e.type == KEYUP:
			if e.key == K_SPACE: direction = (1,0)
		elif e.type == MOUSEBUTTONDOWN:
			if screen.get_at((mx,my))==b_color:
				l = Line((mx,my),direction,10,line_color,3)
				m[mx][my] = 1
				draw_point(screen,mx,my,line_color)
				lines.append(l)
				growing_lines.append(l)
	
	#####CODE TO GROW THE LINES#####################
	to_remove = []
	for l in growing_lines:
		m,growing = l.grow(screen,m,dim)
		if growing == False and l.dead == False:#stopped growing but isn't dead 
			line_counter+=1
			rects = fill_space(l,m,balls)
			total_filled += rect_collision(screen,rects,ballboxes, l.color)
			percent = int((total_filled/(float(dim[0]*dim[1])))*100)
			update_fonts(screen,dim,live_font,p_font,lines_used,lives_num, percent,line_counter)
			to_remove.append(l)
		elif l.dead == True:
			to_remove.append(l)
	for l in to_remove: growing_lines.remove(l)
	##############################################
	i = 0
	for ball in balls:
		ballboxes[i] = ball.bbox
		i+=1
		ball.update(screen,m,dim)
		if ball.bounced == True:
			#means we have a bounce, so check to see if the ball hit a "growing" line
			for l in growing_lines:
				if ball.bbox.colliderect(l.bbox) == True:
					m = l.delete(screen,m, b_color)
					lives_num -= 1
					update_fonts(screen,dim,live_font,p_font,lines_used,lives_num, percent,line_counter)

		update_map(screen,(ball.x-ball.r*2,ball.y-ball.r*2,ball.r*4,ball.r*4),m, line_color)
