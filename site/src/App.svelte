<script>
  const constellations = [
    { name: 'Ursa Major', nickname: 'the Great Bear' },
    { name: 'Ursa Minor', nickname: 'the Little Bear' },
    { name: 'Cassiopeia', nickname: 'the Queen' },
    { name: 'Orion', nickname: 'the Hunter' },
    { name: 'Cygnus', nickname: 'the Swan' },
    { name: 'Lyra', nickname: 'the Lyre' },
    { name: 'Aquila', nickname: 'the Eagle' },
    { name: 'Pegasus', nickname: 'the Winged Horse' },
    { name: 'Andromeda', nickname: 'the Princess' },
    { name: 'Perseus', nickname: 'the Hero' },
    { name: 'Taurus', nickname: 'the Bull' },
    { name: 'Leo', nickname: 'the Lion' },
  ];
</script>

<header>
  <img class="logo" src="/logo.png" alt="Constellia" />
</header>

<main>
  <img class="banner" src="/banniere.jpg" alt="The Big Dipper in the night sky, with its lines" />

  <h1>Recognize the stars in a photo of the sky</h1>
  <p class="soft">
    Constellia is a phone app. It recognizes the constellations in a photo of the night sky,
    then gives the name of every star.
  </p>

  <h2>How it works</h2>
  <ol class="steps">
    <li>
      <strong>You take a photo</strong>
      <p class="soft">Or pick one from your gallery. No network needed.</p>
    </li>
    <li>
      <strong>The AI finds the constellations</strong>
      <p class="soft">A YOLO model, trained on sky maps, draws a box around each constellation it recognizes.</p>
    </li>
    <li>
      <strong>Geometry names the stars</strong>
      <p class="soft">
        The constellation's drawing is fitted onto the stars of the photo. From it we work out where
        the phone was pointing, then name every star in the Hipparcos catalogue.
      </p>
    </li>
  </ol>

  <h2>The 12 constellations it knows</h2>
  <p class="soft">
    The AI was trained to find these constellations, all visible from France. As soon as it finds
    one, the other stars of the photo get their names too.
  </p>
  <ul class="constellations">
    {#each constellations as constellation}
      <li>
        <strong>{constellation.name}</strong>
        <span class="soft">{constellation.nickname}</span>
      </li>
    {/each}
  </ul>
</main>

<style>
  header {
    max-width: 900px;
    margin: 0 auto;
    padding: 16px;
  }

  .logo {
    display: block;
    height: 28px;
    filter: invert(1);
  }

  .banner {
    display: block;
    width: 100%;
    max-height: 360px;
    object-fit: cover;
    border-radius: 24px;
  }

  .steps {
    list-style: none;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 12px;
  }

  .steps li {
    background: var(--night-light);
    border-radius: 24px;
    padding: 20px;
  }

  .steps p {
    margin: 6px 0 0;
  }

  .constellations {
    list-style: none;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
  }

  @media (max-width: 600px) {
    .constellations {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  .constellations li {
    display: flex;
    flex-direction: column;
    background: var(--night-light);
    border-radius: 16px;
    padding: 14px 16px;
  }
</style>
