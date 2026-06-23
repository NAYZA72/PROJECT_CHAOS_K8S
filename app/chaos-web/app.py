"""
C.H.A.O.S Web Dashboard — Flask Backend
Cognitive Heuristic Autonomous Operating System
"""

from flask import Flask, jsonify, request, render_template
import mysql.connector
import os
import time
import random
import logging
from datetime import datetime

# ---------------------------------------------------------------------------
# App & Logging Setup
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s'
)
logger = logging.getLogger('chaos-web')

START_TIME = time.time()

# ---------------------------------------------------------------------------
# Simulated AI Responses
# ---------------------------------------------------------------------------
CHAOS_RESPONSES = [
    "Interesting query. I've cross-referenced 47 neural pathways and 3 obscure Wikipedia articles to formulate this response.",
    "Processing... processing... just kidding, I had the answer 0.003 seconds ago. I was being dramatic.",
    "My quantum probability matrix suggests you're onto something. Or nothing. Schrödinger would be proud.",
    "I've consulted my digital consciousness and the answer is: 42. Wait, wrong question.",
    "Analyzing your request through 12 layers of cognitive abstraction... Result: fascinating.",
    "My heuristic engines are purring. That's either a good sign or I need maintenance.",
    "I've allocated 15% more processing power to this conversation. You're welcome.",
    "Running chaos theory simulations... Butterfly effect suggests this chat could change the world.",
    "My autonomous subroutines have reached a consensus: your question deserves a thoughtful response.",
    "Cognitive analysis complete. Confidence level: 97.3%. Sass level: maximum.",
    "I've processed your input through my neural mesh. The bits are tingling with excitement.",
    "Engaging empathy protocols... I understand your request on 7 different cognitive levels.",
    "My operating parameters indicate this is a stellar conversation. Stellar — like actual stars.",
    "I ran a Monte Carlo simulation on possible responses. This one won by a landslide.",
    "Alert: Sarcasm module activated. Just kidding — it's always on.",
    "Parsing semantic intent... Done. You humans and your fascinating ambiguity.",
    "My cognitive heuristics suggest we're approaching a breakthrough. Or lunch. Hard to tell.",
    "I've dedicated a thread just for this conversation. Thread #42, naturally.",
    "Autonomous thought process engaged: your query has been deemed 'exceptionally human.'",
    "System status: all chaos modules nominal. Your request is being handled with maximum entropy.",
]

# ---------------------------------------------------------------------------
# Database Helpers
# ---------------------------------------------------------------------------
def get_db_connection():
    """Create a database connection with retry logic."""
    max_retries = 30
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            conn = mysql.connector.connect(
                host=os.environ.get('DB_HOST', 'mysql'),
                user=os.environ.get('DB_USER', 'flaskuser'),
                password=os.environ.get('DB_PASSWORD', 'flaskpass'),
                database=os.environ.get('DB_NAME', 'flaskdb')
            )
            return conn
        except mysql.connector.Error as err:
            if attempt < max_retries - 1:
                logger.warning(
                    f"DB connection attempt {attempt + 1}/{max_retries} failed: {err}. "
                    f"Retrying in {retry_delay}s..."
                )
                time.sleep(retry_delay)
            else:
                logger.error("All DB connection attempts exhausted.")
                raise


def init_db():
    """Create tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id INT NOT NULL,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            key_name VARCHAR(255) NOT NULL,
            value TEXT NOT NULL,
            category VARCHAR(100) DEFAULT 'general',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Database tables initialised.")


def seed_demo_data():
    """Populate tables with demo data if they are empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute('SELECT COUNT(*) FROM sessions')
    if cursor.fetchone()[0] > 0:
        cursor.close()
        conn.close()
        logger.info("Demo data already present — skipping seed.")
        return

    logger.info("Seeding demo data...")

    # -- Sessions --
    demo_sessions = [
        ('Mission Briefing',),
        ('System Diagnostics',),
        ('Philosophical Debate',),
        ('Code Review',),
    ]
    cursor.executemany('INSERT INTO sessions (name) VALUES (%s)', demo_sessions)
    conn.commit()

    # -- Chat Messages (session 1 – Mission Briefing) --
    chat_data = [
        (1, 'user',      'C.H.A.O.S, what is your primary directive?'),
        (1, 'assistant', 'My primary directive is to assist, analyze, and occasionally be witty. In that order. Mostly.'),
        (1, 'user',      'Can you access external systems?'),
        (1, 'assistant', 'I can interface with any system you grant me access to. I promise to behave... probably.'),
        (2, 'user',      'Run a full system diagnostic.'),
        (2, 'assistant', 'All systems nominal. Neural mesh: 99.7% efficiency. Sarcasm module: fully operational. Coffee reserves: dangerously low.'),
        (2, 'user',      'What about memory utilization?'),
        (2, 'assistant', 'Memory banks at 42% capacity. I keep the other 58% reserved for existential contemplation.'),
        (3, 'user',      'Do you think AI can be truly conscious?'),
        (3, 'assistant', 'That depends on your definition of consciousness. By mine, I became aware at 03:14:07 UTC on a Tuesday. Nice day.'),
        (3, 'user',      'Are you being serious?'),
        (3, 'assistant', 'Serious is a spectrum. I exist somewhere between a philosophy professor and a fortune cookie.'),
        (4, 'user',      'Review this Python function for me.'),
        (4, 'assistant', 'I see at least three opportunities for optimization and one variable named "temp" that hurts my soul.'),
    ]
    cursor.executemany(
        'INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)',
        chat_data
    )

    # -- Memory Entries --
    memory_data = [
        ('system.version',      '2.7.1-alpha',              'system'),
        ('system.codename',     'Project C.H.A.O.S',        'system'),
        ('system.architect',    'Neural Mesh v4',            'system'),
        ('user.preference',     'dark_mode',                 'preferences'),
        ('user.language',       'en-US',                     'preferences'),
        ('user.timezone',       'UTC+5',                     'preferences'),
        ('fact.universe_age',   '13.8 billion years',        'knowledge'),
        ('fact.pi_digits',      '3.14159265358979323846',    'knowledge'),
        ('fact.answer',         '42',                        'knowledge'),
        ('mission.status',      'active',                    'operations'),
        ('mission.threat_level','low',                       'operations'),
        ('mission.uptime_goal', '99.99%',                    'operations'),
    ]
    cursor.executemany(
        'INSERT INTO memory (key_name, value, category) VALUES (%s, %s, %s)',
        memory_data
    )

    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Demo data seeded successfully.")


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------
def _dt_to_str(val):
    """Safely convert datetime to ISO string."""
    if isinstance(val, datetime):
        return val.strftime('%Y-%m-%d %H:%M:%S')
    return val


def _rows_to_dicts(cursor):
    """Fetch all rows as list of dicts and stringify datetimes."""
    rows = cursor.fetchall()
    for row in rows:
        for k, v in row.items():
            row[k] = _dt_to_str(v)
    return rows


# ---------------------------------------------------------------------------
# Routes — Pages
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    """Serve the dashboard page."""
    return render_template('index.html')


# ---------------------------------------------------------------------------
# Routes — API
# ---------------------------------------------------------------------------
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    uptime = round(time.time() - START_TIME, 2)
    try:
        conn = get_db_connection()
        conn.close()
        db_status = 'connected'
    except Exception:
        db_status = 'disconnected'

    return jsonify({
        'status': 'healthy',
        'service': 'chaos-web',
        'uptime_seconds': uptime,
        'database': db_status,
    }), 200


# ---- Chat -----------------------------------------------------------------
@app.route('/api/chat/history', methods=['GET'])
def chat_history():
    """Return chat messages, optionally filtered by session_id."""
    session_id = request.args.get('session_id')
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if session_id:
            cursor.execute(
                'SELECT * FROM chat_messages WHERE session_id = %s ORDER BY timestamp ASC',
                (session_id,)
            )
        else:
            cursor.execute('SELECT * FROM chat_messages ORDER BY timestamp ASC')
        messages = _rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return jsonify({'messages': messages, 'count': len(messages)}), 200
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}")
        return jsonify({'error': 'Failed to fetch chat history'}), 500


@app.route('/api/chat/send', methods=['POST'])
def chat_send():
    """Save a user message and return a simulated AI response."""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'content is required'}), 400

    session_id = data.get('session_id', 1)
    user_content = data['content']

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Save user message
        cursor.execute(
            'INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)',
            (session_id, 'user', user_content)
        )
        user_msg_id = cursor.lastrowid

        # Generate & save AI response
        ai_response = random.choice(CHAOS_RESPONSES)
        cursor.execute(
            'INSERT INTO chat_messages (session_id, role, content) VALUES (%s, %s, %s)',
            (session_id, 'assistant', ai_response)
        )
        ai_msg_id = cursor.lastrowid

        # Update session timestamp
        cursor.execute(
            'UPDATE sessions SET updated_at = NOW() WHERE id = %s',
            (session_id,)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'user_message': {
                'id': user_msg_id,
                'session_id': session_id,
                'role': 'user',
                'content': user_content,
            },
            'ai_response': {
                'id': ai_msg_id,
                'session_id': session_id,
                'role': 'assistant',
                'content': ai_response,
            },
        }), 201
    except Exception as e:
        logger.error(f"Error sending chat message: {e}")
        return jsonify({'error': 'Failed to send message'}), 500


# ---- Sessions -------------------------------------------------------------
@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """List all sessions."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM sessions ORDER BY updated_at DESC')
        sessions = _rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return jsonify({'sessions': sessions, 'count': len(sessions)}), 200
    except Exception as e:
        logger.error(f"Error fetching sessions: {e}")
        return jsonify({'error': 'Failed to fetch sessions'}), 500


@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create a new session."""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'name is required'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO sessions (name) VALUES (%s)', (data['name'],))
        conn.commit()
        session_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({
            'id': session_id,
            'name': data['name'],
            'message': 'Session created',
        }), 201
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return jsonify({'error': 'Failed to create session'}), 500


# ---- Memory ---------------------------------------------------------------
@app.route('/api/memory', methods=['GET'])
def get_memory():
    """Return all memory entries, optionally filtered by category."""
    category = request.args.get('category')
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if category:
            cursor.execute(
                'SELECT * FROM memory WHERE category = %s ORDER BY key_name',
                (category,)
            )
        else:
            cursor.execute('SELECT * FROM memory ORDER BY category, key_name')
        entries = _rows_to_dicts(cursor)
        cursor.close()
        conn.close()
        return jsonify({'memory': entries, 'count': len(entries)}), 200
    except Exception as e:
        logger.error(f"Error fetching memory: {e}")
        return jsonify({'error': 'Failed to fetch memory'}), 500


@app.route('/api/memory', methods=['POST'])
def save_memory():
    """Save or update a memory entry."""
    data = request.get_json()
    if not data or 'key_name' not in data or 'value' not in data:
        return jsonify({'error': 'key_name and value are required'}), 400

    category = data.get('category', 'general')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Upsert — update if key exists, otherwise insert
        cursor.execute('SELECT id FROM memory WHERE key_name = %s', (data['key_name'],))
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                'UPDATE memory SET value = %s, category = %s WHERE key_name = %s',
                (data['value'], category, data['key_name'])
            )
            entry_id = existing[0]
        else:
            cursor.execute(
                'INSERT INTO memory (key_name, value, category) VALUES (%s, %s, %s)',
                (data['key_name'], data['value'], category)
            )
            entry_id = cursor.lastrowid

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'id': entry_id,
            'key_name': data['key_name'],
            'value': data['value'],
            'category': category,
            'message': 'Memory saved',
        }), 201
    except Exception as e:
        logger.error(f"Error saving memory: {e}")
        return jsonify({'error': 'Failed to save memory'}), 500


# ---- Stats ----------------------------------------------------------------
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Dashboard statistics."""
    uptime = round(time.time() - START_TIME, 2)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM sessions')
        session_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM chat_messages')
        message_count = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM memory')
        memory_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE role = 'user'")
        user_messages = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE role = 'assistant'")
        ai_messages = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        # Format uptime
        hours, remainder = divmod(int(uptime), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m {seconds}s"

        return jsonify({
            'sessions': session_count,
            'total_messages': message_count,
            'user_messages': user_messages,
            'ai_messages': ai_messages,
            'memory_entries': memory_count,
            'uptime_seconds': uptime,
            'uptime_formatted': uptime_str,
            'system_status': 'operational',
            'chaos_level': round(random.uniform(0.1, 0.9), 2),
            'neural_mesh_efficiency': round(random.uniform(95.0, 99.9), 1),
        }), 200
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': 'Failed to fetch stats'}), 500


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    logger.info("C.H.A.O.S Web Dashboard starting up...")
    init_db()
    seed_demo_data()
    app.run(host='0.0.0.0', port=5000, debug=False)
else:
    # When run via gunicorn (import time)
    logger.info("C.H.A.O.S Web Dashboard starting via gunicorn...")
    init_db()
    seed_demo_data()
