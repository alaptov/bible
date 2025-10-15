from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create db instance that will be imported by app.py
db = SQLAlchemy()

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    hebrew_name = db.Column(db.String(100), nullable=False)  # Keep for backward compatibility but won't expose
    paleo_name = db.Column(db.String(100), nullable=False)
    phonetic_name = db.Column(db.String(100))  # Add phonetic name like "barashyt"
    order = db.Column(db.Integer, nullable=False)
    testament = db.Column(db.String(20), nullable=False)  # 'Torah', 'Nevi\'im', 'Ketuvim'
    chapters = db.relationship('Chapter', backref='book', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'paleo_name': self.paleo_name,
            'phonetic_name': self.phonetic_name or self.name.lower(),  # Default to lowercase English name if no phonetic
            'order': self.order,
            'testament': self.testament,
            'chapter_count': len(self.chapters)
        }

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)
    verses = db.relationship('Verse', backref='chapter', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'chapter_number': self.chapter_number,
            'verse_count': len(self.verses)
        }

class Verse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    verse_number = db.Column(db.Integer, nullable=False)
    
    # Original texts
    hebrew_text = db.Column(db.Text, nullable=False)  # Modern Hebrew with nikud
    hebrew_consonantal = db.Column(db.Text, nullable=False)  # Hebrew without nikud
    paleo_text = db.Column(db.Text, nullable=False)  # Paleo Hebrew script
    
    # Transliterations
    paleo_transliteration = db.Column(db.Text, nullable=False)  # Ancient pronunciation (barashyt bara)
    
    # Translations
    english_translation = db.Column(db.Text)  # English translation
    
    # Additional fields
    strong_numbers = db.Column(db.Text)  # Strong's concordance numbers
    morphology = db.Column(db.Text)  # Morphological analysis
    notes = db.Column(db.Text)  # Commentary or notes
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        # Clean paleo text by removing ancient punctuation marks
        clean_paleo_text = self.paleo_text
        if clean_paleo_text:
            # Remove maqqef (־) and sof pasuq (׃) and other ancient punctuation
            ancient_punctuation = ['־', '׃', '׀', '׆']
            for punct in ancient_punctuation:
                clean_paleo_text = clean_paleo_text.replace(punct, '')
        
        # Determine if this is a New Testament book (has Greek text)
        nt_books = [
            'Matthew', 'Mark', 'Luke', 'John', 'Acts',
            'Romans', '1 Corinthians', '2 Corinthians', 'Galatians',
            'Ephesians', 'Philippians', 'Colossians', 
            '1 Thessalonians', '2 Thessalonians', 
            '1 Timothy', '2 Timothy', 'Titus',
            'Philemon', 'Hebrews', 'James', 
            '1 Peter', '2 Peter',
            '1 John', '2 John', '3 John', 
            'Jude', 'Revelation'
        ]
        is_new_testament = self.chapter.book.name in nt_books
        
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'verse_number': self.verse_number,
            'paleo_text': clean_paleo_text,
            'paleo_transliteration': self.paleo_transliteration,
            'english_translation': self.english_translation,
            'strong_numbers': self.strong_numbers,
            'morphology': self.morphology,
            'notes': self.notes,
            'is_new_testament': is_new_testament
        }

class GodFact(db.Model):
    """Model for storing amazing facts that prove God is real"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # science, history, prophecy, miracles, creation
    source = db.Column(db.String(500))  # Reference/source
    
    # Media files (optional)
    image_filename = db.Column(db.String(255))
    video_filename = db.Column(db.String(255))
    
    # Status and metadata
    status = db.Column(db.String(20), default='draft')  # draft, published
    views = db.Column(db.Integer, default=0)
    featured = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'source': self.source,
            'image_filename': self.image_filename,
            'video_filename': self.video_filename,
            'status': self.status,
            'views': self.views,
            'featured': self.featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'image_url': f'/uploads/{self.image_filename}' if self.image_filename else None,
            'video_url': f'/uploads/{self.video_filename}' if self.video_filename else None
        }

class PaleoLetter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    letter = db.Column(db.String(10), nullable=False, unique=True)
    paleo_symbol = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    meaning = db.Column(db.String(200), nullable=False)
    pictograph_description = db.Column(db.String(200), nullable=False)
    sound = db.Column(db.String(20), nullable=False)
    numerical_value = db.Column(db.Integer)
    order = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'letter': self.letter,
            'paleo_symbol': self.paleo_symbol,
            'name': self.name,
            'meaning': self.meaning,
            'pictograph_description': self.pictograph_description,
            'sound': self.sound,
            'numerical_value': self.numerical_value,
            'order': self.order
        }

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hebrew_word = db.Column(db.String(100), nullable=False)
    paleo_word = db.Column(db.String(100), nullable=False)
    transliteration = db.Column(db.String(100), nullable=False)
    pronunciation = db.Column(db.String(100), nullable=False)
    meaning = db.Column(db.Text, nullable=False)
    root_analysis = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hebrew_word': self.hebrew_word,
            'paleo_word': self.paleo_word,
            'transliteration': self.transliteration,
            'pronunciation': self.pronunciation,
            'meaning': self.meaning,
            'root_analysis': self.root_analysis
        }

class StrongsHebrew(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strong_number = db.Column(db.String(20), nullable=False, unique=True)  # H1, H2, etc.
    hebrew_word = db.Column(db.String(100), nullable=False)  # Keep for internal use
    paleo_word = db.Column(db.String(100))  # Paleo Hebrew representation
    transliteration = db.Column(db.String(100), nullable=False)
    pronunciation = db.Column(db.String(100))
    short_definition = db.Column(db.String(200), nullable=False)
    long_definition = db.Column(db.Text)
    usage_count = db.Column(db.Integer, default=0)
    root_word = db.Column(db.String(100))
    part_of_speech = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        from utils.hebrew_converter import hebrew_to_paleo
        # Convert Hebrew to Paleo if not already stored
        paleo_display = self.paleo_word or hebrew_to_paleo(self.hebrew_word)
        
        return {
            'id': self.id,
            'strong_number': self.strong_number,
            'hebrew_word': self.hebrew_word,  # Keep Hebrew for display sequence
            'word': paleo_display,  # Show Paleo instead of Hebrew
            'transliteration': self.transliteration,
            'pronunciation': self.pronunciation,
            'meaning': self.short_definition,
            'definition': self.long_definition or self.short_definition,
            'usage_count': self.usage_count,
            'root_word': self.root_word,
            'part_of_speech': self.part_of_speech
        }

class StrongsGreek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strong_number = db.Column(db.String(20), nullable=False, unique=True)  # G1, G2, etc.
    greek_word = db.Column(db.String(100), nullable=False)
    transliteration = db.Column(db.String(100), nullable=False)
    pronunciation = db.Column(db.String(100))
    short_definition = db.Column(db.String(200), nullable=False)
    long_definition = db.Column(db.Text)
    usage_count = db.Column(db.Integer, default=0)
    root_word = db.Column(db.String(100))
    part_of_speech = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'strong_number': self.strong_number,
            'word': self.greek_word,
            'transliteration': self.transliteration,
            'pronunciation': self.pronunciation,
            'meaning': self.short_definition,
            'definition': self.long_definition or self.short_definition,
            'usage_count': self.usage_count,
            'root_word': self.root_word,
            'part_of_speech': self.part_of_speech
        }
