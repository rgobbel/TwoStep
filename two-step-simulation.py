#!/usr/bin/env python

import numpy as np
import argparse
import pygame
import time
import csv
from itertools import chain

WINDOW = [600, 400]
BACKGROUND = 'gray'

DEBUG = False

HISTORY = None

class NextStateGenerator:
    def __init__(self, params):
        self.params = params
        self.lower_bound = self.params['bounds'][0]
        self.upper_bound = self.params['bounds'][1]
        self.step2flip = self.params['step2flip']

    def get_next(self, prev, counter=0):
        return None

def random_initial(lower, upper):
    return np.random.random() * (upper - lower) + lower

class Brownian(NextStateGenerator):
    def __init__(self, params):
        super().__init__(params)
        self.loc = self.params['loc']
        self.scale = self.params['scale']

    def get_next(self, prev, counter=0):
        next_val = prev + np.random.default_rng().normal(self.params['loc'], self.params['scale'])
        if next_val > self.upper_bound:
            next_val = self.upper_bound - (next_val - self.upper_bound)
        elif next_val < self.lower_bound:
            next_val = self.lower_bound + (self.lower_bound - next_val)
        if DEBUG: print(f'{prev=}, {next_val=}')
        return next_val

    def initial_probs(self):
        vals = np.empty((2,2))
        for i in range(2):
            for j in range(2):
                vals[i,j] = random_initial(self.lower_bound, self.upper_bound)
        return vals

class Blocked(NextStateGenerator):
    def __init__(self, params):
        super().__init__(params)
        self.block_length = self.params['block_length']

    def get_next(self, prev, counter=0):
        if (counter+1) % self.block_length == 0:
            next_val = self.lower_bound if prev == self.upper_bound else self.upper_bound
        else:
            next_val = prev
        return next_val

    def initial_probs(self):
        flip = np.random.randint(2)
        vals = np.empty((2,2))
        for i in range(2):
            vals[i,1-flip] = self.lower_bound
            vals[i,flip] = self.upper_bound
        return vals

GENERATORS = {
    'brownian': Brownian({'step2flip': 0.3, 'bounds': [0.25, 0.75], 'loc': 0.0, 'scale': 0.025}),
    'blocked': Blocked({'step2flip': 0.2, 'bounds': [0.2, 0.8], 'block_length': 10})
}

class ChoiceCard(pygame.sprite.Sprite):
    def __init__(self, image_path, name):
        super().__init__()
        self.image = pygame.transform.scale_by(pygame.image.load(image_path), 0.5)
        self.name = name
        self.rect = self.image.get_rect()
        self.base_rect = self.rect.copy()
        self.pos = tuple(self.base_rect[:2])
        self.base_pos = tuple((self.pos[0], self.pos[1]))
        self._reward_prob = 0.0

    def move(self, pos):
        self.rect.move_ip(pos)
        self.pos = tuple(self.rect[:2])

    def shift(self, offset):
        self.move((offset[0], offset[1]))

    def draw(self, surface, pos=None):
        if pos is None:
            pos = self.pos
        surface.blit(self.image, pos)

    def erase(self, surface):
        pygame.draw.rect(surface, 'gray', self.rect)

    def reset(self):
        self.rect[0] = 0
        self.rect[1] = 0
        self.image.set_alpha(255)

    @property
    def reward_prob(self):
        return self._reward_prob

    @reward_prob.setter
    def reward_prob(self, value):
        self._reward_prob = value

class Trial:
    def __init__(self, task, stims, step2flip, step1_timeout, step2_timeout):
        self.task = task
        self.stims = stims
        self.step2flip = step2flip
        self.step1_timeout = step1_timeout
        self.step2_timeout = step2_timeout

    def run(self):
        self.task.blank_screen()
        # step 1
        valid, step1val, step1choice = self.get_choice(self.stims[0], self.step1_timeout)
        if valid:
            self.animate_choice(self.stims[0], step1val)
        if step1val == pygame.QUIT: # stopping early
            return pygame.QUIT, None, None, None, None
        if not valid:
            if not self.task.args.quiet:
                print('STEP 1 INVALID')
            self.task.blank_screen()
            time.sleep(3)
            return None, None, None, None, None
        step2state = step1val
        if np.random.random() < self.step2flip: # possibly go to less-likely step 2 state
            step2state = 1 - step2state
        # step 2
        valid, step2val, step2choice = self.get_choice(self.stims[step2state+1], self.step2_timeout)
        if not valid:
            if not self.task.args.quiet:
                print('STEP 2 INVALID')
            self.task.blank_screen()
            time.sleep(3)
            return None, None, None, None, None
        self.animate_choice(self.stims[step2state+1], step2val)
        reward = step2choice.reward_prob > np.random.random()
        if reward:
            self.task.window.blit(self.task.winner, self.task.bottom_loc)
        else:
            self.task.window.blit(self.task.loser, self.task.bottom_loc)
        pygame.display.update()
        time.sleep(3)
        return step1val, step1choice, step2val, step2choice, reward

    def get_choice(self, choices, timeout):
        clock = pygame.time.Clock()
        start = pygame.time.get_ticks()
        value = None
        pressed = None
        valid = False
        clock.tick(60)
        margin = 75
        choices[0].reset()
        choices[1].reset()
        choices[0].move((margin, 200))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, pygame.QUIT, None
            if np.any(pygame.key.get_pressed()):
                continue
        choices[0].draw(self.task.window)
        choices[1].move((self.task.width - margin - choices[1].rect.width, 200))
        choices[1].draw(self.task.window)
        # self.task.window.blit(choices[0].image, choices[0].pos)
        # self.task.window.blit(choices[1].image, choices[1].pos)
        pygame.display.flip()
        while value is None:
            event = pygame.event.wait(timeout)
            now = pygame.time.get_ticks()
            if ((now - start) / 1000) > timeout:
                if not self.task.args.quiet:
                    print('TIMEOUT')
                return False, 0, None
            if DEBUG: print(f'{event=}')
            if event.type == pygame.QUIT:
                return False, pygame.QUIT, None
            elif event.type == pygame.KEYDOWN:
                if pressed is None and event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    if DEBUG: print(f'KEYDOWN {event=}')
                    pressed = event.key
                continue
            elif event.type == pygame.KEYUP:
                if event.key == pressed:
                    valid = True
                    value = pressed
                    break
        if value == pygame.K_LEFT:
            value = 0
            if DEBUG: print(f'LEFT, {value=}')
        elif value == pygame.K_RIGHT:
            value = 1
            if DEBUG: print(f'RIGHT, {value=}')
        if value is None:
            return False, None, None
        else:
            return valid, value, choices[value]

    def animate_choice(self, choices, chosen):
        mover = choices[chosen]
        fader = choices[1 - chosen]
        ticks_to_dest = 60
        dest = self.task.top_loc
        alpha_ratio = 255 / ticks_to_dest
        clock = pygame.time.Clock()
        for t in range(ticks_to_dest):
            clock.tick(60)
            fader.erase(self.task.window)
            mover.erase(self.task.window)
            fader.image.set_alpha(int(255 - (t * alpha_ratio)))
            remaining = ticks_to_dest - t
            x_dist = dest[0] - mover.pos[0]
            x_inc = int(x_dist / remaining)
            y_dist = dest[1] - mover.pos[1]
            y_inc = int(y_dist / remaining)
            mover.shift((x_inc, y_inc))
            fader.draw(self.task.window)
            mover.draw(self.task.window)
            pygame.display.update()


def load_choice_cards():
    cards = {}
    images_dir = 'images'
    for step1 in range(2):
        cards[f'Choice1{step1}'] = ChoiceCard(f'{images_dir}/Choice1{step1}.png', f'{step1}')
        for step2 in range(2):
            cards[f'Choice2{step1}{step2}'] = ChoiceCard(f'{images_dir}/Choice2{step1}{step2}.png', f'2{step1}{step2}')
    return cards


class TwoStep:

    def __init__(self, args):
        self.args = args
        self.step1_timeout = args.step1_timeout
        self.step2_timeout = args.step2_timeout
        self.size = self.width, self.height = 640, 400
        self.step2gen = GENERATORS[args.generator]
        step2initial = self.step2gen.initial_probs()
        self.step2flip = self.step2gen.step2flip
        self.cards = load_choice_cards()
        for choice1 in range(2):
            for choice2 in range(2):
                self.cards[f'Choice2{choice1}{choice2}'].reward_prob = step2initial[choice1,choice2]
        self.top_loc = (self.width/2 - self.cards['Choice10'].rect[2]/2, 50)
        self.bottom_loc = (self.width/2 - self.cards['Choice10'].rect[2]/2, 200)
        self.winner = pygame.transform.scale_by(pygame.image.load('images/Winner.png'), 0.5)
        self.loser = pygame.transform.scale_by(pygame.image.load('images/Loser.png'), 0.5)
        pygame.init()
        self.window = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.show_black()
        time.sleep(1)


    def blank_screen(self):
        self.window.fill(BACKGROUND)
        pygame.display.flip()

    def show_black(self):
        self.window.fill('black')
        pygame.display.flip()

    def run_trials(self):
        total_rewards = 0
        history = []
        self.blank_screen()
        time.sleep(5)
        for i_trial in range(self.args.n_trials):
            trial = self.get_next_trial()
            if not self.args.quiet:
                print(f'Trial {i_trial + 1}:')
            step1val, step1choice, step2val, step2choice, reward = trial.run()
            if step1val == pygame.QUIT:
                break
            if step1val is None:
                if not self.args.quiet:
                    print('INVALID')
                continue
            cur_reward = 20 if reward else 0
            total_rewards += cur_reward
            # print(f'1:{step1choice}, 2:{step2choice}, REWARD:{reward}\n')
            if not self.args.quiet:
                print(f'\nREWARD: ${cur_reward:.2f}, AVG: ${total_rewards / (i_trial + 1):.2f}, TOTAL: ${total_rewards:.2f}\n\n')
            reward_probs = [self.cards[f'Choice2{i}{j}'].reward_prob for j in range(2) for i in range(2)]
            history.append([i_trial+1, step1val, step1choice.name, step2val, step2choice.name, reward, reward_probs])
            self.advance(i_trial)
        pygame.quit()
        return history

    def get_next_trial(self):
        stim1order = np.random.randint(2)
        stim20order = np.random.randint(2)
        stim21order = np.random.randint(2)
        stims = [
            [self.cards[f'Choice1{stim1order}'], self.cards[f'Choice1{1 - stim1order}']],
            [self.cards[f'Choice20{stim20order}'], self.cards[f'Choice20{1 - stim20order}']],
            [self.cards[f'Choice21{stim21order}'], self.cards[f'Choice21{1 - stim21order}']]
        ]
        return Trial(self, stims, self.step2flip, self.step1_timeout, self.step2_timeout)

    def advance(self, i_trial):
        for i in range(2):
            for j in range(2):
                self.cards[f'Choice2{i}{j}'].reward_prob = self.step2gen.get_next(self.cards[f'Choice2{i}{j}'].reward_prob, i_trial)

def flatten(l):
    return list(chain.from_iterable(l))
def dump_history(out_name, history):
    with open(f'{out_name}.csv', 'w') as outcsv:
        writer = csv.writer(outcsv)
        writer.writerow(['trial', 'step1val', 'step1choice', 'step2val', 'step2choice', 'reward', 'reward00', 'reward01', 'reward10', 'reward11'])
        for record in history:
            writer.writerow(record[:6]+record[6])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-trials', type=int, default=201, help='Number of trials to run')
    parser.add_argument('--generator', choices=['brownian', 'blocked'], default='brownian', help='Generator type for step 2 reward probabilities')
    parser.add_argument('--step1-timeout', type=int, default=2, help='Timeout for step 1')
    parser.add_argument('--step2-timeout', type=int, default=3, help='Timeout for step 2')
    parser.add_argument('--output', type=str, default='two-step', help='Name of output CSV file')
    parser.add_argument('--quiet', action='store_true', help='Do not print history or running totals')
    args = parser.parse_args()

    task = TwoStep(args)
    history = task.run_trials()
    if not args.quiet:
        print(history)
    dump_history(args.output, history)

if __name__ == '__main__':
    main()