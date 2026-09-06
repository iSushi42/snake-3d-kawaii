"""Procedural kawaii chiptune audio synthesizer and sound effects for 3D Snake."""

import numpy as np
import pygame
from typing import Optional


class KawaiiAudio:
    def __init__(self):
        self.is_enabled = False
        self.is_muted = False
        self.sound_eat: Optional[pygame.mixer.Sound] = None
        self.sound_level_up: Optional[pygame.mixer.Sound] = None
        self.sound_crash: Optional[pygame.mixer.Sound] = None
        self.sound_tick: Optional[pygame.mixer.Sound] = None
        self.sound_pacifier_spawn: Optional[pygame.mixer.Sound] = None
        self.sound_soothe: Optional[pygame.mixer.Sound] = None
        self.sound_bgm: Optional[pygame.mixer.Sound] = None
        self.bgm_channel: Optional[pygame.mixer.Channel] = None

        self._init_mixer_and_sounds()

    def _init_mixer_and_sounds(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._synthesize_all_sounds()
            self.is_enabled = True
            # Allocate a dedicated channel for looping background music
            self.bgm_channel = pygame.mixer.Channel(7)
        except Exception:
            self.is_enabled = False

    def _synthesize_all_sounds(self):
        sample_rate = 44100

        # 1. Eat Apple: Cute ascending "Pop/Nom" chirp (450Hz -> 900Hz, 0.12s)
        dur = 0.12
        n_samples = int(sample_rate * dur)
        t = np.linspace(0, dur, n_samples, endpoint=False)
        freq = np.linspace(450, 920, n_samples)
        envelope = np.exp(-t * 18.0)
        # Soft sine with subtle second harmonic for warmth
        wave = (np.sin(2 * np.pi * freq * t) * 0.7 + np.sin(4 * np.pi * freq * t) * 0.3)
        pcm = (wave * envelope * 15000).astype(np.int16)
        stereo = np.column_stack((pcm, pcm))
        self.sound_eat = pygame.sndarray.make_sound(stereo)

        # 2. Level Up: Cheerful 4-note ascending kawaii fanfare (C5, E5, G5, C6)
        notes = [523.25, 659.25, 783.99, 1046.50]  # Do - Mi - Sol - Do
        note_dur = 0.09
        total_pcm = []
        for i, f in enumerate(notes):
            n_note = int(sample_rate * note_dur)
            t_note = np.linspace(0, note_dur, n_note, endpoint=False)
            env = np.exp(-t_note * 8.0)
            # Gentle vibrato
            vib = 1.0 + 0.015 * np.sin(2 * np.pi * 7.0 * t_note)
            w = (np.sin(2 * np.pi * f * vib * t_note) + 0.3 * np.sin(4 * np.pi * f * t_note))
            pcm_note = (w * env * 14000).astype(np.int16)
            total_pcm.append(pcm_note)
        full_fanfare = np.concatenate(total_pcm)
        stereo_fanfare = np.column_stack((full_fanfare, full_fanfare))
        self.sound_level_up = pygame.sndarray.make_sound(stereo_fanfare)

        # 3. Crash: Cute soft cartoon "Boing / Pouic" descending wobble
        dur_crash = 0.32
        n_crash = int(sample_rate * dur_crash)
        t_crash = np.linspace(0, dur_crash, n_crash, endpoint=False)
        freq_crash = 480 * np.exp(-t_crash * 6.0) + 40 * np.sin(2 * np.pi * 20.0 * t_crash)
        env_crash = np.exp(-t_crash * 5.0)
        w_crash = np.sin(2 * np.pi * freq_crash * t_crash)
        pcm_crash = (w_crash * env_crash * 14000).astype(np.int16)
        stereo_crash = np.column_stack((pcm_crash, pcm_crash))
        self.sound_crash = pygame.sndarray.make_sound(stereo_crash)

        # 4. Timer warning tick (sweet gentle chime)
        dur_tick = 0.06
        n_tick = int(sample_rate * dur_tick)
        t_tick = np.linspace(0, dur_tick, n_tick, endpoint=False)
        w_tick = np.sin(2 * np.pi * 880 * t_tick) * np.exp(-t_tick * 35.0)
        pcm_tick = (w_tick * 10000).astype(np.int16)
        stereo_tick = np.column_stack((pcm_tick, pcm_tick))
        self.sound_tick = pygame.sndarray.make_sound(stereo_tick)

        # 5. Pacifier spawn: Dreamy 2-note bell chime (F5 -> C6)
        spawn_notes = [698.46, 1046.50]
        spawn_dur = 0.15
        pcm_spawn_list = []
        for f in spawn_notes:
            n_sp = int(sample_rate * spawn_dur)
            t_sp = np.linspace(0, spawn_dur, n_sp, endpoint=False)
            env_sp = np.exp(-t_sp * 6.0)
            w_sp = (np.sin(2 * np.pi * f * t_sp) * 0.7 + np.sin(4 * np.pi * f * t_sp) * 0.3)
            pcm_spawn_list.append((w_sp * env_sp * 13000).astype(np.int16))
        full_spawn = np.concatenate(pcm_spawn_list)
        stereo_spawn = np.column_stack((full_spawn, full_spawn))
        self.sound_pacifier_spawn = pygame.sndarray.make_sound(stereo_spawn)

        # 6. Soothe pickup: Relaxing 3-note lullaby chime (G5, E5, C5 with slow soothing decay)
        soothe_notes = [783.99, 659.25, 523.25]
        soothe_dur = 0.18
        pcm_soothe_list = []
        for f in soothe_notes:
            n_so = int(sample_rate * soothe_dur)
            t_so = np.linspace(0, soothe_dur, n_so, endpoint=False)
            env_so = np.exp(-t_so * 4.2)
            vib = 1.0 + 0.01 * np.sin(2 * np.pi * 5.0 * t_so)
            w_so = (np.sin(2 * np.pi * f * vib * t_so) * 0.75 + np.sin(4 * np.pi * f * t_so) * 0.25)
            pcm_soothe_list.append((w_so * env_so * 15000).astype(np.int16))
        full_soothe = np.concatenate(pcm_soothe_list)
        stereo_soothe = np.column_stack((full_soothe, full_soothe))
        self.sound_soothe = pygame.sndarray.make_sound(stereo_soothe)

        # 7. Background Music: Cute, calming 8-bar chiptune loop
        self._synthesize_bgm(sample_rate)

    def _synthesize_bgm(self, sample_rate: int):
        # Sweet kawaii 8-measure lullaby melody (frequencies in Hz)
        # F4, A4, C5, E5 arpeggiated, G4, B4, D5, G5, etc.
        melody_notes = [
            # Bar 1 & 2: F major 7
            349.23, 440.00, 523.25, 659.25, 523.25, 440.00, 659.25, 523.25,
            # Bar 3 & 4: G major
            392.00, 493.88, 587.33, 783.99, 587.33, 493.88, 587.33, 493.88,
            # Bar 5 & 6: E minor 7
            329.63, 392.00, 493.88, 587.33, 493.88, 392.00, 587.33, 493.88,
            # Bar 7 & 8: A minor / C resolve
            440.00, 523.25, 659.25, 880.00, 659.25, 523.25, 587.33, 523.25,
        ]
        beat_dur = 0.22  # ~136 BPM
        total_samples = []

        for note_f in melody_notes:
            n_s = int(sample_rate * beat_dur)
            t_s = np.linspace(0, beat_dur, n_s, endpoint=False)
            # Soft bell/music box envelope: fast attack, gentle decay
            env_s = np.exp(-t_s * 4.2)
            # Soft sine + quiet octave
            wave_s = np.sin(2 * np.pi * note_f * t_s) * 0.75 + np.sin(4 * np.pi * note_f * t_s) * 0.25
            total_samples.append((wave_s * env_s * 4500).astype(np.int16))

        full_bgm = np.concatenate(total_samples)
        stereo_bgm = np.column_stack((full_bgm, full_bgm))
        self.sound_bgm = pygame.sndarray.make_sound(stereo_bgm)

    def play_eat(self):
        if self.is_enabled and not self.is_muted and self.sound_eat:
            self.sound_eat.play()

    def play_level_up(self):
        if self.is_enabled and not self.is_muted and self.sound_level_up:
            self.sound_level_up.play()

    def play_crash(self):
        if self.is_enabled and not self.is_muted and self.sound_crash:
            self.sound_crash.play()

    def play_tick(self):
        if self.is_enabled and not self.is_muted and self.sound_tick:
            self.sound_tick.play()

    def play_pacifier_spawn(self):
        if self.is_enabled and not self.is_muted and self.sound_pacifier_spawn:
            self.sound_pacifier_spawn.play()

    def play_soothe(self):
        if self.is_enabled and not self.is_muted and self.sound_soothe:
            self.sound_soothe.play()

    def start_bgm(self):
        if self.is_enabled and not self.is_muted and self.sound_bgm and self.bgm_channel:
            if not self.bgm_channel.get_busy():
                self.bgm_channel.play(self.sound_bgm, loops=-1)

    def stop_bgm(self):
        if self.bgm_channel:
            self.bgm_channel.stop()

    def toggle_mute(self) -> bool:
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.stop_bgm()
        else:
            self.start_bgm()
        return self.is_muted


# Backwards compatibility alias
DoomAudio = KawaiiAudio
