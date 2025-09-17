import os
import argparse
import numpy as np
import wave
import struct
import platform

def midi_to_freq(midi_note):
    """
    Převod MIDI noty na frekvenci.
    Používá standardní ladění: A4 (nota 69) = 440 Hz.
    """
    return 440.0 * (2 ** ((midi_note - 69) / 12.0))

def db_to_amp(db):
    """
    Převod dB na faktor amplitudy.
    Používá vzorec: 10^(dB/20).
    """
    return 10 ** (db / 20.0)

def generate_sine_wave(sample_rate, duration, frequency, amplitude):
    """
    Generuje sine vlnu jako NumPy array.
    - sample_rate: Frekvence vzorkování (Hz).
    - duration: Délka v sekundách.
    - frequency: Frekvence sine vlny (Hz).
    - amplitude: Faktor amplitudy (0-1, kde 1 = max pro 16-bit).
    Vrátí array signed 16-bit integer hodnot pro stereo (interleaved).
    """
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)
    # Převod na 16-bit signed int (-32768 až 32767)
    sine_wave_int = np.int16(sine_wave * 32767)
    # Stereo: Duplikuj pro levý a pravý kanál (identické)
    stereo_wave = np.column_stack((sine_wave_int, sine_wave_int)).flatten()
    return stereo_wave

def save_wav_file(filename, sample_rate, data):
    """
    Uloží data jako WAV soubor.
    - filename: Cesta k souboru.
    - sample_rate: Frekvence vzorkování.
    - data: NumPy array s interleaved stereo daty (16-bit).
    """
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        # Převod na bytes (struct.pack pro interleaved data)
        wav_data = b''.join([struct.pack('<h', val) for val in data])
        wav_file.writeframes(wav_data)

def get_default_output_dir():
    """
    Vrátí defaultní výstupní adresář podle OS.
    - Windows:      C:/SoundBanks/IthacaPlayer/instrument
    - Linux/Mac:    ~/Soundbank/IthacaPlayer/instrument/
    """
    if platform.system() == 'Windows':
        return r'C:\\SoundBanks\\IthacaPlayer\\instrument'
    else:
        return os.path.expanduser('~/Soundbank/IthacaPlayer/instrument')

def main():
    """
    Hlavní funkce programu.
    Parsuje argumenty, vytvoří adresář a generuje WAV soubory pro MIDI noty 21-108.
    """
    parser = argparse.ArgumentParser(description='Generuje WAV soubory s sine vlnami pro MIDI noty.')
    parser.add_argument('--output-dir', type=str, help='Výstupní adresář pro soubory.')
    args = parser.parse_args()

    output_dir = args.output_dir if args.output_dir else get_default_output_dir()
    os.makedirs(output_dir, exist_ok=True)  # Vytvoř adresář, pokud neexistuje

    sample_rates = [44100, 48000]  # Hz
    rate_tags = {44100: '44', 48000: '48'}  # fZZ
    duration = 5.0  # Sekundy
    db_levels = np.linspace(-30, -6, 8)  # Od nejslabší (-30 dB) po nejhlasitější (-6 dB)

    for midi_note in range(21, 109):  # MIDI noty 21-108 (A0 až C8)
        freq = midi_to_freq(midi_note)
        note_str = f'm{midi_note:03d}'  # mXXX

        for vel in range(8):  # Velocity 0-7
            db = db_levels[vel]
            amp = db_to_amp(db)
            print(f'Generuji: Nota {note_str}, Velocity {vel}, Hlasitost {db:.1f} dB, Frekvence {freq:.2f} Hz')

            for sample_rate in sample_rates:
                data = generate_sine_wave(sample_rate, duration, freq, amp)
                filename = f'{note_str}-vel{vel}-f{rate_tags[sample_rate]}.wav'
                filepath = os.path.join(output_dir, filename)
                save_wav_file(filepath, sample_rate, data)

    print(f'Generování dokončeno. Soubory uloženy do: {output_dir}')

if __name__ == '__main__':
    main()