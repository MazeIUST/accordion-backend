import random


# Users
USERS = [
    {
        'username': 'mhhasani',
        'first_name': 'mohammadhosein',
        'last_name': 'hasani',
        'password': '1234',
        'email': 'hasanimohammadhosein@gmail.com',
        'is_email_verified': True,
        'is_Artist': True,
        'birthday': '2002-09-18',
        'country': 'Iran',
        'city': 'Tehran',
        'image': '/media/profiles/photos/mhhasani.jpg',
    },
    {
        'username': 'melika',
        'first_name': 'melika',
        'last_name': 'mohammadi',
        'password': '1234',
        'email': 'melikamfakhar@gmail.com',
        'is_email_verified': True,
        'is_Artist': True,
        'birthday': '2002-11-20',
        'country': 'Iran',
        'city': 'Qom',
        'image': '/media/profiles/photos/melika.jpg',
    },
    {
        'username': 'zahra',
        'first_name': 'zahra',
        'last_name': 'tabatabaei',
        'password': '1234',
        'email': 'zahrasadat@gmail.com',
        'is_email_verified': True,
        'is_Artist': True,
        'birthday': '2002-09-16',
        'country': 'Iran',
        'city': 'Tehran',
        'image': '/media/profiles/photos/zahra.jpg',
    },
    {
        'username': 'maryam',
        'first_name': 'maryam',
        'last_name': 'jafari',
        'password': '1234',
        'email': 'maryamjafari@gmail.com',
        'is_email_verified': True,
        'is_Artist': True,
        'birthday': '2002-09-11',
        'country': 'Iran',
        'city': 'Yazd',
        'image': '/media/profiles/photos/maryam.jpg',
    },
    {
        'username': 'mojtaba',
        'first_name': 'mojtaba',
        'last_name': 'janbaz',
        'password': '1234',
        'email': 'mojtabajanbaz@gmail.com',
        'is_email_verified': True,
        'is_Artist': True,
        'birthday': '2002-08-27',
        'country': 'Iran',
        'city': 'Mazandaran',
        'image': '/media/profiles/photos/mojtaba.jpg',
    },
    {
        'username': 'amirmohammad',
        'first_name': 'amirmohammad',
        'last_name': 'khorshidi',
        'password': '1234',
        'email': 'amirmohammadkhorshidi@gmail.com',
        'is_email_verified': True,
        'is_Artist': True,
        'birthday': '2002-03-26',
        'country': 'Iran',
        'city': 'Tehran',
        'image': '/media/profiles/photos/amirmohammad.jpg',
    },
]

CITIES = ['Tehran', 'Qom', 'Yazd', 'Mazandaran', 'Isfahan', 'Shiraz', 'Kerman', 'Kermanshah', 'Khorasan', 'Gilan',
          'Golestan', 'Hormozgan', 'Kohgiluyeh and Boyer-Ahmad', 'Kurdistan', 'Lorestan', 'Markazi', 'Mazandaran',
          'North Khorasan', 'Qazvin', 'Qom', 'Semnan', 'Sistan and Baluchestan', 'South Khorasan', 'Tehran',
          'West Azarbaijan', 'Yazd', 'Zanjan', 'Alborz', 'Ardabil', 'Bushehr', 'Chaharmahal and Bakhtiari', 'East Azarbaijan',
          'Fars', 'Golestan', 'Hamadan', 'Hormozgan', 'Ilam', 'Kerman', 'Kermanshah', 'Khuzestan', 'Kohgiluyeh and Boyer-Ahmad',
          'Kurdistan', 'Lorestan', 'Markazi', 'Mazandaran', 'North Khorasan', 'Qazvin', 'Qom', 'Semnan', 'Sistan and Baluchestan',
          'South Khorasan', 'Tehran', 'West Azarbaijan', 'Yazd', 'Zanjan', 'Alborz', 'Ardabil', 'Bushehr', 'Chaharmahal and Bakhtiari',
          'East Azarbaijan', 'Fars', 'Golestan', 'Hamadan', 'Hormozgan', 'Ilam', 'Kerman', 'Kermansh']

TAGS = ['pop', 'rock', 'jazz', 'classical', 'hip-hop', 'rap',
        'country', 'folk', 'blues', 'metal', 'punk', 'soul', 'r&b', 'disco']


def make_user():
    users = USERS
    for i in range(100):
        user = {
            'username': f'user{i}',
            'first_name': f'user{i}',
            'last_name': f'user{i}',
            'password': '1234',
            'email': 'user1@gmail.com',
            'is_email_verified': True,
            'is_Artist': i % 5 == 0,
            'birthday': f'{random.randint(1950, 2002)}-{random.randint(1, 12)}-{random.randint(1, 28)}',
            'country': 'Iran',
            'city': random.choice(CITIES),
            'image': f'/media/profiles/photos/user{i}.jpg',
        }
        users.append(user)

    return users
