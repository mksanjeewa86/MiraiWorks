# MiraiWorks Code Review Guidelines

## 📋 Pull Request Requirements

### 1. Documentation
- [ ] Code is well-commented using JSDoc/docstring standards
- [ ] API changes are documented in OpenAPI/Swagger
- [ ] README updates if needed
- [ ] Changelog entry added
- [ ] Type definitions are complete and accurate

### 2. Testing
- [ ] Unit tests cover new functionality
- [ ] Integration tests for API changes
- [ ] Test coverage meets minimum requirements (90%)
- [ ] Edge cases are tested
- [ ] Error scenarios are covered

### 3. Code Quality
- [ ] Follows project architecture (CLAUDE.md)
- [ ] No code smells or anti-patterns
- [ ] Consistent naming conventions
- [ ] No unnecessary complexity
- [ ] Efficient database queries
- [ ] No hardcoded values

### 4. Security
- [ ] Input validation is thorough
- [ ] Authentication/authorization checked
- [ ] No sensitive data exposure
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection where needed

### 5. Performance
- [ ] No N+1 queries
- [ ] Appropriate indexing for queries
- [ ] Efficient data structures used
- [ ] Resource-intensive operations optimized
- [ ] Caching strategy where appropriate

## 🔍 Review Process

### Before Review
1. Run all tests locally
2. Check code formatting
3. Verify CI/CD pipeline passes
4. Self-review using checklist

### During Review
1. Read the description and requirements
2. Check out the branch locally
3. Test the changes manually
4. Review code using checklist
5. Provide constructive feedback

### Review Comments
- Be specific and clear
- Explain why, not just what
- Suggest improvements
- Link to documentation/resources
- Use a collaborative tone

### Response to Reviews
- Address all comments
- Explain complex changes
- Update code based on feedback
- Request re-review when ready

## 🚫 Common Issues to Watch For

### Backend
1. **Architecture Violations**
   - Business logic in endpoints
   - Database queries in services
   - Missing input validation

2. **Database Issues**
   - Missing indexes
   - Inefficient queries
   - Transaction handling
   - Connection management

3. **Security Issues**
   - Missing authentication
   - Improper authorization
   - Unvalidated input
   - Unsafe data handling

### Frontend
1. **React/Next.js Best Practices**
   - Unnecessary re-renders
   - Memory leaks
   - Proper hook usage
   - Component composition

2. **TypeScript**
   - Type safety
   - Interface definitions
   - Generic usage
   - Type assertions

3. **Performance**
   - Bundle size
   - Code splitting
   - Image optimization
   - State management

## ✅ Review Checklist Template

```markdown
### General
- [ ] Code follows project architecture
- [ ] Documentation is complete
- [ ] Tests are comprehensive
- [ ] Performance is optimized
- [ ] Security is addressed

### Specific Areas
- [ ] Input validation
- [ ] Error handling
- [ ] Logging
- [ ] Configuration
- [ ] Dependencies

### Code Quality
- [ ] DRY principles
- [ ] SOLID principles
- [ ] Clean Code practices
- [ ] Consistent styling
- [ ] Clear naming

### Security
- [ ] Authentication
- [ ] Authorization
- [ ] Data validation
- [ ] Error messages
- [ ] Sensitive data

### Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Edge cases
- [ ] Error scenarios
- [ ] Coverage
```

## 🎯 Review Completion Criteria

1. All checklist items addressed
2. CI/CD pipeline passes
3. Test coverage meets requirements
4. Documentation is complete
5. Security review passed
6. Performance criteria met

## 📈 Continuous Improvement

- Review guidelines quarterly
- Update based on team feedback
- Track common issues
- Share learnings in team meetings
- Update documentation regularly
