const frenchNames = {
  'Ursa Major': 'Grande Ourse',
  'Ursa Minor': 'Petite Ourse',
  'Cassiopeia': 'Cassiopée',
  'Orion': 'Orion',
  'Cygnus': 'Cygne',
  'Lyra': 'Lyre',
  'Aquila': 'Aigle',
  'Pegasus': 'Pégase',
  'Andromeda': 'Andromède',
  'Perseus': 'Persée',
  'Taurus': 'Taureau',
  'Leo': 'Lion',
};

String frenchName(String constellation) => frenchNames[constellation] ?? constellation;
