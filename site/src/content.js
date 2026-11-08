/*
 * ─────────────────────────────────────────────────────────────────────────────
 *  EDIT THIS FILE to personalise the greeting. It is the only file you need.
 * ─────────────────────────────────────────────────────────────────────────────
 *  - Plain text only. Markup is never interpreted (everything is set with
 *    textContent), so "<b>" will appear literally.
 *  - If you change the headline, message, Hindi line, sign-off or blessing,
 *    also update the matching text inside <main> in site/index.html. That copy
 *    is what visitors see when JavaScript is unavailable, and what link
 *    previews read.
 *  - Never put private information here: this file is public on GitHub Pages.
 */
window.DIWALI_CONTENT = Object.freeze({
  sender: 'Abhishek',

  recipient: {
    // Salutation reads: "<greetingWord> <fallback>,"
    greetingWord: 'Dear',
    fallback: 'friends and family'
  },

  eyebrow: 'A light from my home to yours',

  threshold: {
    line: 'A little light is waiting for you.',
    button: 'Light the diya'
  },

  headline: 'Happy Diwali',

  // Approved line only. Do not replace with machine translation.
  hindiLine: 'दीपावली की हार्दिक शुभकामनाएँ',

  message:
    'May every light you kindle bring warmth to your home, courage to your heart, ' +
    'and joy to the paths we share. Wishing you and your loved ones a Diwali filled ' +
    'with peace, laughter, good health, and bright new beginnings.',

  signoff: 'With warmth,',

  blessing:
    'From my home to yours, may the light stay with you long after the lamps grow quiet.',

  momentsTitle: 'Little moments that light up the year',

  /*
   * The festival wall. See ASSETS.md for preparing images.
   *  src:          'assets/photos/<file>' (leave '' to show a placeholder)
   *  still:        for a .gif only: a still frame for reduced motion and Pause
   *  shape:        'round' | 'arch' | 'polaroid' | 'wide' | 'square' | 'cutout'
   *  slot:         'a' to 'g', a position on the wall (see .moment--slot-* in styles.css)
   *  width/height: the real pixel size of the file (prevents layout shift)
   *  alt:          describe what is in the image for someone who cannot see it
   *  caption, when, where: short, optional
   */
  moments: [
    {
      src: 'assets/photos/diyas-bokeh.webp',
      shape: 'square',
      slot: 'a',
      width: 1208,
      height: 1210,
      alt: 'Painted clay diyas in pink, blue, green and gold burn on a table, with warm orange lights glowing out of focus behind them.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/moment-1.webp',
      shape: 'round',
      slot: 'b',
      width: 886,
      height: 886,
      alt: 'A round rangoli of red, orange and yellow lotus petals with two blue peacocks at its sides, and seven lit clay diyas placed around it on a marble floor.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/diyas-marigold.webp',
      shape: 'arch',
      slot: 'c',
      width: 1174,
      height: 1400,
      alt: 'Seven lit diyas with pink, green and blue bead-work rims are arranged around a cluster of yellow marigolds on red and green velvet.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/moment-2.webp',
      shape: 'wide',
      slot: 'd',
      width: 1280,
      height: 964,
      alt: 'A stone path at night runs under strings of paper lanterns, between curtains of gold and pink fairy lights and lamp shapes made of glowing wire.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/rangoli-crescent.webp',
      shape: 'arch',
      slot: 'e',
      width: 990,
      height: 1400,
      alt: 'A crescent-shaped flower rangoli of deep red petals, white buds and orange and yellow marigolds, with a brass diya at its centre and small lit diyas placed around it on the floor.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/moment-5.webp',
      shape: 'round',
      slot: 'f',
      width: 840,
      height: 936,
      alt: 'A tangled loop of red fairy lights glows against dark green leaves at night.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/diyas-tealights.webp',
      shape: 'polaroid',
      slot: 'g',
      width: 863,
      height: 1400,
      alt: 'Lit tealight diyas in gold holders, some with green and red wax, around a brass bowl holding a floating flower candle and rose petals, beside a small Ganesha idol.',
      caption: '',
      when: '',
      where: ''
    }
  ],

  share: {
    title: 'Happy Diwali',
    text: 'A little light is waiting for you.'
  },

  sound: {
    // The song clip that plays and loops. To change it, put a licensed file in
    // site/assets/audio/ and change this path (see "Changing the song" in ASSETS.md).
    // '' = an original raga-style loop synthesised in the browser instead.
    // Now playing: "Jai Raghuvanshi Ayodhyapati Ram Chandra Ki Jai", 0:07 to 0:25,
    // used under the owner's licence.
    src: 'assets/audio/jai-raghuvanshi-loop.m4a',
    loop: true,
    // true: music starts when the visitor clicks "Light the diya".
    // false: music stays off until the visitor turns on the Music button.
    startOnLight: true,
    // 0.05 to 0.6. Music always fades in to this level.
    volume: 0.35
  },

  features: {
    // Set to false to hide the photo wall.
    moments: true,
    // Looping music with a Music on/off button. Nothing plays before the first click.
    sound: true,
    // Share button (Web Share API) with a copy-link fallback.
    share: true,
    hindiLine: true,
    // 'full' | 'gentle' | 'minimal'. Visitors who prefer reduced motion
    // always get the minimal, static version.
    animation: 'full'
  }
});
