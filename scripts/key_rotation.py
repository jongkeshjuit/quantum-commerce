# security/incident_response.py
"""
SECURITY INCIDENT RESPONSE SYSTEM
Tự động phát hiện và response các security incidents
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class IncidentType(Enum):
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    CRYPTO_ATTACK = "crypto_attack"
    DATA_BREACH = "data_breach"
    KEY_COMPROMISE = "key_compromise"
    REPLAY_ATTACK = "replay_attack"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    SYSTEM_COMPROMISE = "system_compromise"

class SecurityIncident:
    """Security incident object"""
    
    def __init__(self, incident_type: IncidentType, severity: IncidentSeverity, 
                 description: str, source_ip: str = None, user_id: str = None):
        self.id = f"INC_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(description) % 10000:04d}"
        self.incident_type = incident_type
        self.severity = severity
        self.description = description
        self.source_ip = source_ip
        self.user_id = user_id
        self.timestamp = datetime.utcnow()
        self.status = "open"
        self.response_actions = []
        self.resolved_at = None

class IncidentResponseSystem:
    """Automated security incident response"""
    
    def __init__(self):
        self.incidents = {}  # In production: use database
        self.response_rules = self._load_response_rules()
        self.notification_config = self._load_notification_config()
        
    def _load_response_rules(self) -> Dict[str, Any]:
        """Load automated response rules"""
        return {
            IncidentType.UNAUTHORIZED_ACCESS: {
                'auto_actions': ['block_ip', 'invalidate_sessions', 'alert_admin'],
                'escalation_time_minutes': 15,
                'requires_manual_review': True
            },
            IncidentType.CRYPTO_ATTACK: {
                'auto_actions': ['emergency_key_rotation', 'block_ip', 'alert_security_team'],
                'escalation_time_minutes': 5,
                'requires_manual_review': True
            },
            IncidentType.DATA_BREACH: {
                'auto_actions': ['isolate_systems', 'emergency_key_rotation', 'notify_authorities'],
                'escalation_time_minutes': 1,
                'requires_manual_review': True
            },
            IncidentType.KEY_COMPROMISE: {
                'auto_actions': ['emergency_key_rotation', 'invalidate_all_sessions', 'alert_security_team'],
                'escalation_time_minutes': 2,
                'requires_manual_review': True
            },
            IncidentType.REPLAY_ATTACK: {
                'auto_actions': ['block_ip', 'invalidate_session', 'alert_admin'],
                'escalation_time_minutes': 10,
                'requires_manual_review': False
            },
            IncidentType.RATE_LIMIT_EXCEEDED: {
                'auto_actions': ['temporary_ip_block', 'alert_admin'],
                'escalation_time_minutes': 30,
                'requires_manual_review': False
            }
        }
    
    def _load_notification_config(self) -> Dict[str, Any]:
        """Load notification configuration"""
        return {
            'security_team_email': ['security@quantum-commerce.com'],
            'admin_email': ['admin@quantum-commerce.com'],
            'slack_security_channel': '#security-alerts',
            'pagerduty_integration': True,
            'sms_alerts': ['+1234567890']  # For critical incidents
        }
    
    async def report_incident(self, incident_type: IncidentType, severity: IncidentSeverity,
                            description: str, context: Dict[str, Any] = None) -> SecurityIncident:
        """Report và process security incident"""
        
        # Create incident
        incident = SecurityIncident(
            incident_type=incident_type,
            severity=severity,
            description=description,
            source_ip=context.get('source_ip') if context else None,
            user_id=context.get('user_id') if context else None
        )
        
        # Store incident
        self.incidents[incident.id] = incident
        
        logger.critical(f"🚨 SECURITY INCIDENT: {incident.id} - {incident.incident_type.value}")
        logger.critical(f"   Severity: {incident.severity.value}")
        logger.critical(f"   Description: {incident.description}")
        
        # Trigger automated response
        await self._trigger_automated_response(incident, context)
        
        # Send notifications
        await self._send_incident_notifications(incident)
        
        return incident
    
    async def _trigger_automated_response(self, incident: SecurityIncident, context: Dict[str, Any] = None):
        """Trigger automated response actions"""
        
        rules = self.response_rules.get(incident.incident_type)
        if not rules:
            logger.warning(f"No response rules for {incident.incident_type.value}")
            return
        
        logger.warning(f"🤖 Triggering automated response for {incident.id}")
        
        for action in rules['auto_actions']:
            try:
                success = await self._execute_response_action(action, incident, context)
                
                incident.response_actions.append({
                    'action': action,
                    'timestamp': datetime.utcnow().isoformat(),
                    'success': success,
                    'automated': True
                })
                
                if success:
                    logger.info(f"✅ Executed response action: {action}")
                else:
                    logger.error(f"❌ Failed response action: {action}")
                    
            except Exception as e:
                logger.error(f"❌ Response action {action} failed: {e}")
    
    async def _execute_response_action(self, action: str, incident: SecurityIncident, 
                                     context: Dict[str, Any] = None) -> bool:
        """Execute specific response action"""
        
        try:
            if action == 'block_ip':
                return await self._block_ip(incident.source_ip)
            
            elif action == 'temporary_ip_block':
                return await self._temporary_ip_block(incident.source_ip, minutes=30)
            
            elif action == 'invalidate_sessions':
                return await self._invalidate_user_sessions(incident.user_id)
            
            elif action == 'invalidate_all_sessions':
                return await self._invalidate_all_sessions()
            
            elif action == 'emergency_key_rotation':
                return await self._emergency_key_rotation(incident.description)
            
            elif action == 'isolate_systems':
                return await self._isolate_affected_systems(context)
            
            elif action == 'alert_admin':
                return await self._alert_administrators(incident)
            
            elif action == 'alert_security_team':
                return await self._alert_security_team(incident)
            
            elif action == 'notify_authorities':
                return await self._notify_authorities(incident)
            
            else:
                logger.warning(f"Unknown response action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Response action {action} error: {e}")
            return False
    
    async def _block_ip(self, ip_address: str) -> bool:
        """Block IP address permanently"""
        if not ip_address:
            return False
        
        # In production: update firewall rules, WAF, etc.
        logger.warning(f"🚫 BLOCKING IP: {ip_address}")
        
        # Add to blocked IPs list
        from security.security_middleware import security_middleware
        security_middleware.suspicious_ips.add(ip_address)
        
        return True
    
    async def _temporary_ip_block(self, ip_address: str, minutes: int = 30) -> bool:
        """Temporarily block IP address"""
        if not ip_address:
            return False
        
        logger.warning(f"⏰ TEMPORARY BLOCK: {ip_address} for {minutes} minutes")
        
        # Implementation: temporary block logic
        # Could use Redis with TTL
        
        return True
    
    async def _invalidate_user_sessions(self, user_id: str) -> bool:
        """Invalidate all sessions for specific user"""
        if not user_id:
            return False
        
        logger.warning(f"🔓 INVALIDATING SESSIONS for user: {user_id}")
        
        try:
            from services.session_service import session_service
            count = session_service.destroy_all_user_sessions(int(user_id))
            logger.info(f"✅ Invalidated {count} sessions for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Session invalidation failed: {e}")
            return False
    
    async def _invalidate_all_sessions(self) -> bool:
        """Invalidate ALL active sessions (nuclear option)"""
        logger.critical("☢️  INVALIDATING ALL SESSIONS (NUCLEAR OPTION)")
        
        try:
            from services.session_service import session_service
            # Implementation: clear all session keys from Redis
            # session_service.redis_client.flushdb()
            
            logger.critical("✅ All sessions invalidated")
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate all sessions: {e}")
            return False
    
    async def _emergency_key_rotation(self, reason: str) -> bool:
        """Emergency rotation of all cryptographic keys"""
        logger.critical(f"🔄 EMERGENCY KEY ROTATION: {reason}")
        
        try:
            from scripts.key_rotation import KeyRotationManager
            rotation_manager = KeyRotationManager()
            await rotation_manager.emergency_rotate_all_keys(reason)
            return True
        except Exception as e:
            logger.error(f"Emergency key rotation failed: {e}")
            return False
    
    async def _isolate_affected_systems(self, context: Dict[str, Any] = None) -> bool:
        """Isolate affected systems from network"""
        logger.critical("🏝️ ISOLATING AFFECTED SYSTEMS")
        
        # Implementation would:
        # 1. Identify affected containers/services
        # 2. Remove from load balancer
        # 3. Block network access
        # 4. Create isolated environment for forensics
        
        return True
    
    async def _alert_administrators(self, incident: SecurityIncident) -> bool:
        """Alert system administrators"""
        message = f"""
🚨 SECURITY ALERT - {incident.severity.value.upper()}

Incident ID: {incident.id}
Type: {incident.incident_type.value}
Time: {incident.timestamp}
Description: {incident.description}
Source IP: {incident.source_ip or 'N/A'}
User ID: {incident.user_id or 'N/A'}

Immediate actions taken:
{chr(10).join([f"- {action['action']}" for action in incident.response_actions])}

Please review and take additional action if needed.
        """
        
        # Send email/slack notifications
        await self._send_notification(message, self.notification_config['admin_email'])
        return True
    
    async def _alert_security_team(self, incident: SecurityIncident) -> bool:
        """Alert security team"""
        message = f"""
🚨 CRITICAL SECURITY INCIDENT

ID: {incident.id}
Severity: {incident.severity.value.upper()}
Type: {incident.incident_type.value}
Time: {incident.timestamp}

{incident.description}

Automated response triggered. Manual review required.
        """
        
        # Send to security team
        await self._send_notification(message, self.notification_config['security_team_email'])
        
        # Send SMS for critical incidents
        if incident.severity == IncidentSeverity.CRITICAL:
            await self._send_sms_alert(message)
        
        return True
    
    async def _notify_authorities(self, incident: SecurityIncident) -> bool:
        """Notify authorities for data breaches"""
        logger.critical("🏛️ NOTIFYING AUTHORITIES - DATA BREACH")
        
        # Implementation would:
        # 1. Prepare incident report
        # 2. Send to regulatory bodies (GDPR, etc.)
        # 3. Notify law enforcement if required
        # 4. Document all communications
        
        return True
    
    async def _send_notification(self, message: str, recipients: List[str]):
        """Send notification via email/slack"""
        logger.info(f"📨 Sending notification to {len(recipients)} recipients")
        # Implementation: actual email/slack sending
    
    async def _send_sms_alert(self, message: str):
        """Send SMS alert for critical incidents"""
        logger.info("📱 Sending SMS alert")
        # Implementation: SMS gateway integration
    
    async def _send_incident_notifications(self, incident: SecurityIncident):
        """Send notifications based on incident severity"""
        
        if incident.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH]:
            await self._alert_security_team(incident)
        
        if incident.severity == IncidentSeverity.CRITICAL:
            # Page security team immediately
            logger.critical(f"📟 PAGING SECURITY TEAM - {incident.id}")
        
        # Always alert admins
        await self._alert_administrators(incident)
    
    def get_incident_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get incident statistics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent_incidents = [
            inc for inc in self.incidents.values()
            if inc.timestamp >= cutoff_date
        ]
        
        stats = {
            'total_incidents': len(recent_incidents),
            'by_severity': {},
            'by_type': {},
            'resolved_count': 0,
            'avg_resolution_time_hours': 0
        }
        
        # Count by severity
        for severity in IncidentSeverity:
            count = len([inc for inc in recent_incidents if inc.severity == severity])
            stats['by_severity'][severity.value] = count
        
        # Count by type
        for incident_type in IncidentType:
            count = len([inc for inc in recent_incidents if inc.incident_type == incident_type])
            stats['by_type'][incident_type.value] = count
        
        # Resolution stats
        resolved = [inc for inc in recent_incidents if inc.resolved_at]
        stats['resolved_count'] = len(resolved)
        
        if resolved:
            total_resolution_time = sum([
                (inc.resolved_at - inc.timestamp).total_seconds() / 3600
                for inc in resolved
            ])
            stats['avg_resolution_time_hours'] = total_resolution_time / len(resolved)
        
        return stats
    
    async def resolve_incident(self, incident_id: str, resolution_notes: str):
        """Mark incident as resolved"""
        if incident_id in self.incidents:
            incident = self.incidents[incident_id]
            incident.status = "resolved"
            incident.resolved_at = datetime.utcnow()
            
            logger.info(f"✅ Incident {incident_id} resolved: {resolution_notes}")
            
            # Send resolution notification
            await self._send_resolution_notification(incident, resolution_notes)

    async def _send_resolution_notification(self, incident: SecurityIncident, notes: str):
        """Send incident resolution notification"""
        message = f"""
✅ INCIDENT RESOLVED

ID: {incident.id}
Type: {incident.incident_type.value}
Resolved: {incident.resolved_at}
Resolution: {notes}

Total duration: {incident.resolved_at - incident.timestamp}
        """
        
        await self._send_notification(message, self.notification_config['admin_email'])

# Global incident response system
incident_response = IncidentResponseSystem()

# Convenience functions for common incidents
async def report_unauthorized_access(source_ip: str, user_id: str = None, details: str = ""):
    """Report unauthorized access attempt"""
    return await incident_response.report_incident(
        IncidentType.UNAUTHORIZED_ACCESS,
        IncidentSeverity.HIGH,
        f"Unauthorized access attempt: {details}",
        {'source_ip': source_ip, 'user_id': user_id}
    )

async def report_crypto_attack(attack_type: str, source_ip: str = None, details: str = ""):
    """Report cryptographic attack"""
    return await incident_response.report_incident(
        IncidentType.CRYPTO_ATTACK,
        IncidentSeverity.CRITICAL,
        f"Crypto attack detected: {attack_type} - {details}",
        {'source_ip': source_ip}
    )

async def report_data_breach(affected_users: int, data_types: List[str], details: str = ""):
    """Report data breach"""
    return await incident_response.report_incident(
        IncidentType.DATA_BREACH,
        IncidentSeverity.CRITICAL,
        f"Data breach: {affected_users} users affected, data: {', '.join(data_types)} - {details}",
        {'affected_users': affected_users, 'data_types': data_types}
    )

# CLI for incident management
async def main():
    """CLI for incident management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Security Incident Response')
    parser.add_argument('action', choices=['list', 'stats', 'resolve', 'test'])
    parser.add_argument('--incident-id', help='Incident ID for resolution')
    parser.add_argument('--notes', help='Resolution notes')
    parser.add_argument('--days', type=int, default=30, help='Days for statistics')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        print("🚨 RECENT SECURITY INCIDENTS")
        print("=" * 60)
        
        recent_incidents = sorted(
            incident_response.incidents.values(),
            key=lambda x: x.timestamp,
            reverse=True
        )[:10]
        
        for incident in recent_incidents:
            print(f"\n{incident.id}")
            print(f"  Type: {incident.incident_type.value}")
            print(f"  Severity: {incident.severity.value}")
            print(f"  Time: {incident.timestamp}")
            print(f"  Status: {incident.status}")
            print(f"  Description: {incident.description}")
            if incident.source_ip:
                print(f"  Source IP: {incident.source_ip}")
            print(f"  Actions: {len(incident.response_actions)} automated")
    
    elif args.action == 'stats':
        print("📊 INCIDENT STATISTICS")
        print("=" * 40)
        
        stats = incident_response.get_incident_statistics(args.days)
        
        print(f"Last {args.days} days:")
        print(f"Total incidents: {stats['total_incidents']}")
        print(f"Resolved: {stats['resolved_count']}")
        print(f"Avg resolution time: {stats['avg_resolution_time_hours']:.1f} hours")
        
        print("\nBy Severity:")
        for severity, count in stats['by_severity'].items():
            print(f"  {severity}: {count}")
        
        print("\nBy Type:")
        for incident_type, count in stats['by_type'].items():
            if count > 0:
                print(f"  {incident_type}: {count}")
    
    elif args.action == 'resolve':
        if not args.incident_id or not args.notes:
            print("❌ Incident ID and resolution notes required")
            return
        
        await incident_response.resolve_incident(args.incident_id, args.notes)
        print(f"✅ Incident {args.incident_id} marked as resolved")
    
    elif args.action == 'test':
        print("🧪 TESTING INCIDENT RESPONSE SYSTEM")
        print("=" * 50)
        
        # Test different incident types
        test_incidents = [
            (IncidentType.RATE_LIMIT_EXCEEDED, IncidentSeverity.LOW, "Test rate limit"),
            (IncidentType.UNAUTHORIZED_ACCESS, IncidentSeverity.HIGH, "Test unauthorized access"),
            (IncidentType.CRYPTO_ATTACK, IncidentSeverity.CRITICAL, "Test crypto attack")
        ]
        
        for incident_type, severity, description in test_incidents:
            incident = await incident_response.report_incident(
                incident_type, severity, description,
                {'source_ip': '192.168.1.100', 'user_id': 'test_user'}
            )
            print(f"✅ Created test incident: {incident.id}")
            
            # Auto-resolve test incidents
            await incident_response.resolve_incident(incident.id, "Test incident - auto resolved")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())