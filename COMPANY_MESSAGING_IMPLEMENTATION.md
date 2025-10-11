# Company-Based Messaging Implementation

## 📋 Overview

Messages are sent **between connections** (companies/entities), not individual users. The message displays:
- **Primary**: The company/entity sending
- **Secondary**: The actual user who sent it

### Example Display

```
┌─────────────────────────────────────┐
│ 🏢 Company A • John Doe             │
│ "Hello, we are interested in your  │
│  profile for our open position..."  │
│                                     │
│ 2:30 PM                             │
└─────────────────────────────────────┘
```

---

## 🗃️ Database Schema Updates

### 1. Update `messages` Table

```sql
ALTER TABLE messages
ADD COLUMN sender_entity_type ENUM('user', 'company') NOT NULL DEFAULT 'user' COMMENT 'Type of sending entity',
ADD COLUMN sender_company_id INT NULL COMMENT 'Company sending the message',
ADD COLUMN recipient_entity_type ENUM('user', 'company') NOT NULL DEFAULT 'user' COMMENT 'Type of receiving entity',
ADD COLUMN recipient_company_id INT NULL COMMENT 'Company receiving the message',
ADD COLUMN sent_on_behalf_of_company BOOLEAN DEFAULT FALSE COMMENT 'Message sent on behalf of company',

ADD FOREIGN KEY (sender_company_id) REFERENCES companies(id) ON DELETE SET NULL,
ADD FOREIGN KEY (recipient_company_id) REFERENCES companies(id) ON DELETE SET NULL,

ADD INDEX idx_sender_company (sender_company_id),
ADD INDEX idx_recipient_company (recipient_company_id);
```

### Current Structure
```
sender_id (user) → recipient_id (user)
```

### New Structure
```
sender_id (actual user who sent)
sender_entity_type (user or company)
sender_company_id (if company is sender)

→

recipient_id (target user, nullable for company recipients)
recipient_entity_type (user or company)
recipient_company_id (if company is recipient)
```

---

## 🏗️ Updated Message Model

```python
# backend/app/models/message.py
class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Actual sender (always a user who clicked send)
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    # Sender entity (who the message is FROM)
    sender_entity_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="user"
    )
    sender_company_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("companies.id"), nullable=True
    )

    # Recipient entity (who the message is TO)
    recipient_entity_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="user"
    )
    recipient_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    recipient_company_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("companies.id"), nullable=True
    )

    # Message content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(20), default="text")

    # Metadata
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now)

    # Relationships
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    sender_company: Mapped["Company | None"] = relationship(
        "Company", foreign_keys=[sender_company_id]
    )
    recipient_user: Mapped["User | None"] = relationship(
        "User", foreign_keys=[recipient_id]
    )
    recipient_company: Mapped["Company | None"] = relationship(
        "Company", foreign_keys=[recipient_company_id]
    )

    @property
    def sender_display_name(self) -> str:
        """Get display name for sender."""
        if self.sender_entity_type == "company" and self.sender_company:
            return self.sender_company.name
        return self.sender.full_name

    @property
    def recipient_display_name(self) -> str:
        """Get display name for recipient."""
        if self.recipient_entity_type == "company" and self.recipient_company:
            return self.recipient_company.name
        if self.recipient_user:
            return self.recipient_user.full_name
        return "Unknown"
```

---

## 🔄 Message Sending Logic

### Scenario 1: User from Company A → Individual Candidate

```python
# User A (from Company A) sends to Candidate B
message = Message(
    sender_id=user_a_id,                    # Actual user who sent
    sender_entity_type="company",            # Sent as Company A
    sender_company_id=company_a_id,          # Company A

    recipient_entity_type="user",            # To individual
    recipient_id=candidate_b_id,             # Candidate B
    recipient_company_id=None,

    content="We are interested in your profile..."
)
```

**Display:**
```
From: Company A (via User A)
To: Candidate B
```

### Scenario 2: Company A → Company B (any user)

```python
# User A (from Company A) sends to Company B
message = Message(
    sender_id=user_a_id,                    # Actual user who sent
    sender_entity_type="company",            # Sent as Company A
    sender_company_id=company_a_id,          # Company A

    recipient_entity_type="company",         # To company
    recipient_id=None,                       # No specific user
    recipient_company_id=company_b_id,       # Company B

    content="We would like to discuss a partnership..."
)
```

**Display:**
```
From: Company A (via User A)
To: Company B
```

### Scenario 3: Individual → Company

```python
# Candidate A sends to Company B
message = Message(
    sender_id=candidate_a_id,               # Actual user who sent
    sender_entity_type="user",               # Sent as individual
    sender_company_id=None,

    recipient_entity_type="company",         # To company
    recipient_id=None,                       # No specific user
    recipient_company_id=company_b_id,       # Company B

    content="I'm interested in your job opening..."
)
```

**Display:**
```
From: Candidate A
To: Company B
```

---

## 🎯 Updated Message Service

```python
# backend/app/services/message_service.py
class MessageService:
    async def send_message(
        self,
        db: AsyncSession,
        sender_id: int,
        message_data: MessageCreate
    ) -> Message:
        """
        Send a message between connections.

        Message data should include:
        - recipient_entity_type: 'user' or 'company'
        - recipient_id: user ID (if sending to user)
        - recipient_company_id: company ID (if sending to company)
        """

        # Get sender with company
        sender = await db.execute(
            select(User)
            .options(selectinload(User.company))
            .where(User.id == sender_id)
        )
        sender = sender.scalar_one()

        # Determine sender entity
        if sender.company_id:
            sender_entity_type = "company"
            sender_company_id = sender.company_id
        else:
            sender_entity_type = "user"
            sender_company_id = None

        # Validate connection exists
        await self._validate_connection(
            db,
            sender_entity_type=sender_entity_type,
            sender_user_id=sender_id,
            sender_company_id=sender_company_id,
            recipient_entity_type=message_data.recipient_entity_type,
            recipient_id=message_data.recipient_id,
            recipient_company_id=message_data.recipient_company_id
        )

        # Create message
        message = Message(
            sender_id=sender_id,
            sender_entity_type=sender_entity_type,
            sender_company_id=sender_company_id,

            recipient_entity_type=message_data.recipient_entity_type,
            recipient_id=message_data.recipient_id,
            recipient_company_id=message_data.recipient_company_id,

            content=message_data.content,
            type=message_data.type
        )

        db.add(message)
        await db.commit()
        await db.refresh(message)

        return message

    async def _validate_connection(
        self,
        db: AsyncSession,
        sender_entity_type: str,
        sender_user_id: int,
        sender_company_id: int | None,
        recipient_entity_type: str,
        recipient_id: int | None,
        recipient_company_id: int | None
    ):
        """Validate that a connection exists between sender and recipient."""

        # Use company_connection_service to check
        connection_exists = await company_connection_service.check_connection(
            db,
            source_type=sender_entity_type,
            source_user_id=sender_user_id if sender_entity_type == "user" else None,
            source_company_id=sender_company_id,
            target_type=recipient_entity_type,
            target_user_id=recipient_id,
            target_company_id=recipient_company_id
        )

        if not connection_exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No connection exists. Please connect first."
            )
```

---

## 📱 Frontend Updates

### 1. Updated Message Schema

```typescript
// frontend/src/types/message.ts
interface Message {
  id: number;

  // Actual sender (user who clicked send)
  sender_id: number;
  sender_name: string;
  sender_email: string;

  // Sender entity (company or user)
  sender_entity_type: 'user' | 'company';
  sender_company_id?: number;
  sender_company_name?: string;

  // Recipient entity (company or user)
  recipient_entity_type: 'user' | 'company';
  recipient_id?: number;
  recipient_name?: string;
  recipient_company_id?: number;
  recipient_company_name?: string;

  content: string;
  type: 'text' | 'file' | 'system';
  is_read: boolean;
  created_at: string;
}

interface MessageSendRequest {
  recipient_entity_type: 'user' | 'company';
  recipient_id?: number;        // Required if recipient_entity_type = 'user'
  recipient_company_id?: number; // Required if recipient_entity_type = 'company'
  content: string;
  type?: 'text' | 'file';
}
```

### 2. Message Display Component

```tsx
// frontend/src/components/messages/MessageBubble.tsx
interface MessageBubbleProps {
  message: Message;
  isOwnMessage: boolean;
}

export function MessageBubble({ message, isOwnMessage }: MessageBubbleProps) {
  // Determine display name
  const displayName = message.sender_entity_type === 'company'
    ? message.sender_company_name
    : message.sender_name;

  const actualSender = message.sender_name;

  return (
    <div className={`message-bubble ${isOwnMessage ? 'own' : 'other'}`}>
      {/* Header with entity name and actual sender */}
      <div className="message-header">
        {message.sender_entity_type === 'company' ? (
          <div className="flex items-center gap-2">
            <CompanyIcon className="h-5 w-5" />
            <span className="font-semibold">{displayName}</span>
            <span className="text-gray-500">•</span>
            <span className="text-sm text-gray-600">{actualSender}</span>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <UserIcon className="h-5 w-5" />
            <span className="font-semibold">{displayName}</span>
          </div>
        )}
      </div>

      {/* Message content */}
      <div className="message-content">
        {message.content}
      </div>

      {/* Timestamp */}
      <div className="message-time">
        {formatTime(message.created_at)}
      </div>
    </div>
  );
}
```

### 3. Updated Conversations List

```tsx
// Group conversations by company/entity, not individual users
interface Conversation {
  entity_type: 'user' | 'company';
  entity_id: number;
  entity_name: string;
  entity_company_name?: string;

  last_message: Message;
  unread_count: number;
  last_activity: string;

  // All users from this entity who have sent messages
  participants: Array<{
    id: number;
    name: string;
    email: string;
  }>;
}

// Display in conversations list
<div className="conversation-item">
  {conversation.entity_type === 'company' ? (
    <>
      <CompanyAvatar name={conversation.entity_name} />
      <div className="conversation-info">
        <h3>{conversation.entity_name}</h3>
        <p className="last-message">
          <span className="sender">{conversation.last_message.sender_name}:</span>
          {conversation.last_message.content}
        </p>
        <p className="participants">
          {conversation.participants.length} members
        </p>
      </div>
    </>
  ) : (
    <>
      <UserAvatar name={conversation.entity_name} />
      <div className="conversation-info">
        <h3>{conversation.entity_name}</h3>
        <p className="last-message">
          {conversation.last_message.content}
        </p>
      </div>
    </>
  )}

  {conversation.unread_count > 0 && (
    <Badge>{conversation.unread_count}</Badge>
  )}
</div>
```

---

## 🎨 UI Mockups

### Conversation List View

```
┌─────────────────────────────────────────────┐
│  Inbox                                      │
├─────────────────────────────────────────────┤
│                                             │
│  🏢 TechCorp Recruitment        [2]         │
│     John Doe: We have reviewed your...     │
│     3 members • 2:45 PM                     │
│                                             │
│  🏢 StartupXYZ                              │
│     Sarah Lee: Thank you for your...       │
│     5 members • Yesterday                   │
│                                             │
│  👤 Alice Johnson                           │
│     I'm interested in the position...      │
│     11:30 AM                                │
│                                             │
└─────────────────────────────────────────────┘
```

### Chat View

```
┌─────────────────────────────────────────────┐
│  🏢 TechCorp Recruitment                    │
│  John Doe, Sarah Lee, Mike Chen (3)        │
├─────────────────────────────────────────────┤
│                                             │
│     ┌────────────────────────────┐         │
│     │ 🏢 TechCorp • John Doe     │         │
│     │ We have reviewed your      │         │
│     │ profile and would like     │         │
│     │ to discuss further...      │         │
│     │           2:30 PM          │         │
│     └────────────────────────────┘         │
│                                             │
│  ┌────────────────────────────┐            │
│  │ You                        │            │
│  │ Thank you for reaching     │            │
│  │ out! I'd love to discuss.  │            │
│  │           2:35 PM          │            │
│  └────────────────────────────┘            │
│                                             │
│     ┌────────────────────────────┐         │
│     │ 🏢 TechCorp • Sarah Lee    │         │
│     │ Great! Let me send you     │         │
│     │ the details...             │         │
│     │           2:40 PM          │         │
│     └────────────────────────────┘         │
│                                             │
├─────────────────────────────────────────────┤
│  [Type message...]              [Send]     │
└─────────────────────────────────────────────┘
```

---

## 🔐 Permission Rules

### Who Can Send Messages?

1. **Individual → Company**:
   - ✅ If connection exists
   - Message goes to ALL users in that company

2. **Company User → Individual**:
   - ✅ If connection exists
   - Message displays as from Company (via User)

3. **Company User → Company**:
   - ✅ If company-to-company connection exists
   - Message goes to ALL users in target company
   - Displays as from Company (via User)

### Who Can See Messages?

1. **Messages TO a company**:
   - ✅ All users in that company can see
   - ✅ Messages grouped in one conversation thread

2. **Messages FROM a company**:
   - ✅ Recipient sees company name + actual sender
   - ✅ All messages in same thread regardless of which user sent

---

## 📊 Database Queries

### Get Conversations for User

```sql
-- Get all conversations where user's company is involved
SELECT DISTINCT
    CASE
        WHEN m.sender_entity_type = 'company' AND m.sender_company_id = :user_company_id
        THEN m.recipient_entity_type
        WHEN m.recipient_entity_type = 'company' AND m.recipient_company_id = :user_company_id
        THEN m.sender_entity_type
    END as other_entity_type,

    CASE
        WHEN m.sender_entity_type = 'company' AND m.sender_company_id = :user_company_id
        THEN COALESCE(m.recipient_company_id, m.recipient_id)
        WHEN m.recipient_entity_type = 'company' AND m.recipient_company_id = :user_company_id
        THEN COALESCE(m.sender_company_id, 0)
    END as other_entity_id,

    MAX(m.created_at) as last_activity,
    COUNT(CASE WHEN m.is_read = FALSE AND m.recipient_company_id = :user_company_id THEN 1 END) as unread_count
FROM messages m
WHERE
    (m.sender_company_id = :user_company_id OR m.recipient_company_id = :user_company_id)
GROUP BY other_entity_type, other_entity_id
ORDER BY last_activity DESC;
```

---

## ✅ Migration Checklist

- [ ] Update messages table schema
- [ ] Create Message model with new fields
- [ ] Update MessageService for connection-based sending
- [ ] Update message validation to check company connections
- [ ] Update frontend Message type definition
- [ ] Create MessageBubble component with company display
- [ ] Update conversations list to group by entity
- [ ] Update API endpoints to accept entity-based recipients
- [ ] Create migration script for existing messages
- [ ] Update tests for new message model
- [ ] Update documentation

---

## 🚀 Implementation Order

1. **Phase 1**: Update database schema and models
2. **Phase 2**: Update backend message service
3. **Phase 3**: Update API endpoints
4. **Phase 4**: Update frontend types and API client
5. **Phase 5**: Update message display components
6. **Phase 6**: Update conversations list
7. **Phase 7**: Test and deploy

---

**Last Updated**: 2025-10-11
**Status**: Implementation Ready
**Version**: 2.0
