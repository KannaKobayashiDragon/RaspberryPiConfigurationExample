import json
import boto3
import uuid
import time
import random
from decimal import Decimal

# Initialize DynamoDB Resource Instance
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('AuditSessions')

def generate_short_unique_id():
    """
    Generate a short but unique identifier (8 characters)
    Format: <timestamp_last6><random_2chars>
    """
    timestamp_part = str(int(time.time()))[-6:]
    random_part = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=2))
    return f"{timestamp_part}{random_part}"

def generate_random_string(length=8):
    """
    Generate random alphanumeric string for HID typing
    """
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choices(chars, k=length))

def generate_random_script():
    """
    Generate action script in both formats:
    1. action_script (JSON array for DynamoDB readability)
    2. action_code (string format for Android simplicity)
    
    Pattern: Type → Wait 2-3s → Delete → Wait 2-3s → Repeat (2-3 times)
    """
    action_script = []
    code_parts = []
    total_time = 0.0
    
    # Generate 2-3 sequences
    num_sequences = random.randint(2, 3)
    
    for i in range(num_sequences):
        # 1. Type random HID string
        string_length = random.randint(6, 10)
        random_string = generate_random_string(string_length)
        
        action_script.append({
            "cmd": "HID",
            "params": {
                "action": "TYPE",
                "text": random_string
            }
        })
        code_parts.append(f'H"{random_string}"')
        
        # 2. Wait 2-5 seconds
        wait_time = round(random.uniform(2.0, 5.0), 1)
        action_script.append({
            "cmd": "WAIT",
            "params": {"seconds": Decimal(str(wait_time))}
        })
        code_parts.append(f'W{wait_time}')
        total_time += wait_time
        
        # 3. Delete the HID string
        action_script.append({
            "cmd": "HID",
            "params": {
                "action": "DELETE",
                "count": string_length
            }
        })
        code_parts.append(f'D{string_length}')
        
        # 4. Wait 2-3 seconds after deletion
        post_delete_wait = round(random.uniform(2.0, 5.0), 1)
        action_script.append({
            "cmd": "WAIT",
            "params": {"seconds": Decimal(str(post_delete_wait))}
        })
        code_parts.append(f'W{post_delete_wait}')
        total_time += post_delete_wait
    
    # Final wait before key press
    final_wait = round(random.uniform(2.0, 5.0), 1)
    action_script.append({
        "cmd": "WAIT",
        "params": {"seconds": Decimal(str(final_wait))}
    })
    code_parts.append(f'W{final_wait}')
    total_time += final_wait
    
    # Final key press
    key_choice = random.choice(["UP", "DOWN","LEFT","RIGHT"])
    action_script.append({
        "cmd": "HID",
        "params": {
            "action": "PRESS",
            "key": key_choice
        }
    })
    code_parts.append(f'K"{key_choice}"')
    
    # Join all parts with semicolon for action_code
    action_code = ';'.join(code_parts)
    
    return action_script, action_code, round(total_time, 1)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        # Generate session_id (short and unique)
        session_id = generate_short_unique_id()
        
        # Timestamps
        created_at = int(time.time())
        ttl = created_at + 600  # 10 minutes TTL
        
        # Generate both formats
        action_script, action_code, estimated_duration = generate_random_script()
        
        # Generate audit video name
        audit_video_name = f"{session_id}.mp4"
        
        # Prepare DynamoDB item (with readable JSON array)
        item = {
            'session_id': session_id,
            'created_at': created_at,
            'ttl': ttl,
            'action_script': action_script,  # JSON array for database readability
            'status': 'CREATED',
            'verified': False,
            'audit_video_name': audit_video_name
        }
        
        # Insert into DynamoDB
        table.put_item(Item=item)
        
        # Prepare API response (with simplified string format)
        response_body = {
            "session_id": session_id,
            "payload_type": "RAW_CHALLENGE",
            "timestamp": created_at,
            "audit_video_name": audit_video_name,
            "estimated_duration": estimated_duration,
            "data": {
                "action_code": action_code  # String format for Android
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_body, cls=DecimalEncoder)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal Server Error',
                'details': str(e)
            })
        }