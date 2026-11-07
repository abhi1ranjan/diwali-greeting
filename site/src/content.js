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
    // Salutation reads: "<greetingWord> <name from ?to=, or fallback>,"
    greetingWord: 'Dear',
    fallback: 'friends and family',
    // Optional URL personalisation, e.g. .../diwali-greeting/?to=Ananya
    // Set features.urlPersonalization to false to ignore the parameter.
    param: 'to'
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

  momentsNote: 'The rangoli art, diya pictures and fireworks here were drawn by computer. They are illustrations, not real footage.',

  /*
   * The festival wall. See ASSETS.md for preparing images.
   *  src:          'assets/photos/<file>' (leave '' to show a placeholder)
   *  still:        for a .gif only: a still frame, shown when the visitor prefers
   *                reduced motion, presses Pause, or has scrolled away
   *  shape:        'round' | 'arch' | 'polaroid' | 'wide' | 'square' | 'cutout'
   *  slot:         'a' to 'p', a position on the wall (see .moment--slot-* in styles.css)
   *  width/height: the real pixel size of the file (prevents layout shift)
   *  alt:          describe what is in the image for someone who cannot see it
   *  caption, when, where: short, optional
   */
  moments: [
    {
      src: 'assets/photos/fireworks-nagaoka.gif',
      still: 'assets/photos/fireworks-nagaoka-still.webp',
      shape: 'wide',
      slot: 'a',
      width: 540,
      height: 360,
      alt: 'Illustration: rockets rise over a dark river valley and open into a row of coloured shells, then one giant gold shell spreads across the sky.',
      caption: 'Inspired by the Nagaoka Fireworks Festival, Japan',
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
      src: 'assets/photos/fireworks-spring-festival.gif',
      still: 'assets/photos/fireworks-spring-festival-still.webp',
      shape: 'arch',
      slot: 'c',
      width: 400,
      height: 500,
      alt: 'Illustration: a long string of red firecrackers crackles beside red paper lanterns while red and gold shells burst in the sky.',
      caption: 'Inspired by the Spring Festival, China',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/art-rangoli-lotus.webp',
      shape: 'cutout',
      slot: 'd',
      width: 900,
      height: 900,
      alt: 'Illustration: a rangoli of pink and gold lotus petals with teal leaves on a cream base.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/moment-2.webp',
      shape: 'wide',
      slot: 'e',
      width: 1280,
      height: 964,
      alt: 'A stone path at night runs under strings of paper lanterns, between curtains of gold and pink fairy lights and lamp shapes made of glowing wire.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/art-rangoli-peacock.webp',
      shape: 'cutout',
      slot: 'f',
      width: 900,
      height: 900,
      alt: 'Illustration: a rangoli wheel of peacock feathers in teal, gold and violet on deep blue.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/moment-3.webp',
      shape: 'polaroid',
      slot: 'g',
      width: 666,
      height: 705,
      alt: 'A sign on a wall in red lettering reads: Love, Always. For every kind of love, there\'s a seat at the table.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/fireworks-city-tower.gif',
      still: 'assets/photos/fireworks-city-tower-still.webp',
      shape: 'arch',
      slot: 'h',
      width: 400,
      height: 500,
      alt: 'Illustration: sparks shoot out from every level of a very tall, slender tower above a city skyline, followed by bursts around its spire.',
      caption: 'Inspired by New Year\'s Eve in Dubai, UAE',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/moment-4.webp',
      shape: 'polaroid',
      slot: 'i',
      width: 310,
      height: 552,
      alt: 'A tall floral arrangement on a black pedestal, with white lilies, blue orchids and a dome of purple chrysanthemums, in a marble hotel lobby.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/art-rangoli-kolam.webp',
      shape: 'cutout',
      slot: 'j',
      width: 900,
      height: 900,
      alt: 'Illustration: a kolam of white looping lines and gold dots on an earth-brown circle, ringed by white petals.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/fireworks-harbour.gif',
      still: 'assets/photos/fireworks-harbour-still.webp',
      shape: 'wide',
      slot: 'k',
      width: 540,
      height: 360,
      alt: 'Illustration: a curtain of sparks pours from an arched bridge into a harbour while shells burst above it and sail-like shapes stand on the shore.',
      caption: 'Inspired by New Year\'s Eve in Sydney, Australia',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/moment-5.webp',
      shape: 'round',
      slot: 'l',
      width: 840,
      height: 936,
      alt: 'A tangled loop of red fairy lights glows against dark green leaves at night.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/fireworks-beehive.gif',
      still: 'assets/photos/fireworks-beehive-still.webp',
      shape: 'square',
      slot: 'm',
      width: 420,
      height: 420,
      alt: 'Illustration: hundreds of rockets streak out in every direction from a rack on the ground, above the silhouettes of a watching crowd.',
      caption: 'Inspired by the Yanshui Beehive Fireworks Festival, Taiwan',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/art-rangoli-flowers.webp',
      shape: 'cutout',
      slot: 'n',
      width: 900,
      height: 900,
      alt: 'Illustration: a flower-carpet rangoli of concentric orange, yellow, maroon and green rings.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/art-rangoli-diya-star.webp',
      shape: 'cutout',
      slot: 'o',
      width: 900,
      height: 900,
      alt: 'Illustration: an eight-pointed red and gold star rangoli on blue, with a small lit diya at each point.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/diya-marigold.webp',
      shape: 'arch',
      slot: 'q',
      width: 900,
      height: 1100,
      alt: 'Illustration: seven lit diyas decorated with rings of pink, blue and gold beads, set around a cluster of yellow marigolds on red and green velvet.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/rangoli-crescent.webp',
      shape: 'round',
      slot: 'r',
      width: 1000,
      height: 1000,
      alt: 'Illustration: a crescent-moon rangoli of deep red petals edged with white buds and marigolds, with a fan of orange petals and a brass diya inside, ringed by small lit diyas.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/diya-bokeh.webp',
      shape: 'wide',
      slot: 's',
      width: 1200,
      height: 800,
      alt: 'Illustration: five painted clay diyas burn on a table, with warm orange lights glowing out of focus behind them.',
      caption: '',
      when: '',
      where: ''
    },
    {
      src: 'assets/photos/fireworks-diwali-ground.gif',
      still: 'assets/photos/fireworks-diwali-ground-still.webp',
      shape: 'wide',
      slot: 'p',
      width: 540,
      height: 360,
      alt: 'Illustration: gold fountains rise from clay pots and spinning wheels throw sparks on the ground, in front of a low wall lined with small diyas.',
      caption: 'Anar and chakri on the ground at Diwali',
      when: '',
      where: ''
    }
  ],

  share: {
    title: 'Happy Diwali',
    text: 'A little light is waiting for you.'
  },

  sound: {
    // The song that plays and loops. To change it, put a licensed file in
    // site/assets/audio/ and change this path (see "Changing the song" in ASSETS.md).
    // '' = an original raga-style loop synthesised in the browser instead.
    // Now playing: "Shaam Rangoli Si Raatein Taaron Wali" by Vishal Mishra,
    // used under the owner's licence.
    src: 'assets/audio/diwali-song.m4a',
    loop: true,
    // true: music starts when the visitor clicks "Light the diya".
    // false: music stays off until the visitor turns on the Music button.
    startOnLight: true,
    // 0.05 to 0.6. Music always fades in to this level.
    volume: 0.35
  },

  features: {
    // Set to false to hide the festival wall of photos and fireworks.
    moments: true,
    // Looping music with a Music on/off button. Nothing plays before the first click.
    sound: true,
    // Share button (Web Share API) with a copy-link fallback.
    share: true,
    hindiLine: true,
    urlPersonalization: true,
    // 'full' | 'gentle' | 'minimal'. Visitors who prefer reduced motion
    // always get the minimal, static version.
    animation: 'full'
  }
});
