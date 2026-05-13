/**
 * Authorization
 * 
 * Role-based access control and permission checking
 */

export type Role = 'user' | 'admin' | 'system'
export type Permission = 'read' | 'write' | 'execute' | 'admin'

export interface User {
  id: string
  role: Role
  permissions: Permission[]
}

export interface AuthzConfig {
  requiredRole?: Role
  requiredPermission?: Permission
  allowSystem?: boolean
}

export class Authorization {
  /**
   * Check if user has required role
   */
  static hasRole(user: User, requiredRole: Role): boolean {
    const roleHierarchy: Record<Role, number> = {
      user: 1,
      admin: 2,
      system: 3,
    }

    return roleHierarchy[user.role] >= roleHierarchy[requiredRole]
  }

  /**
   * Check if user has required permission
   */
  static hasPermission(user: User, requiredPermission: Permission): boolean {
    return user.permissions.includes(requiredPermission) || user.permissions.includes('admin')
  }

  /**
   * Authorize user for action
   */
  static authorize(
    user: User,
    config: AuthzConfig
  ): { authorized: boolean; error?: string } {
    const { requiredRole, requiredPermission, allowSystem = true } = config

    // System user bypass (if allowed)
    if (user.role === 'system' && allowSystem) {
      return { authorized: true }
    }

    // Check role
    if (requiredRole && !this.hasRole(user, requiredRole)) {
      return {
        authorized: false,
        error: `Required role: ${requiredRole}, user role: ${user.role}`,
      }
    }

    // Check permission
    if (requiredPermission && !this.hasPermission(user, requiredPermission)) {
      return {
        authorized: false,
        error: `Required permission: ${requiredPermission}`,
      }
    }

    return { authorized: true }
  }

  /**
   * Create system user (for internal operations)
   */
  static createSystemUser(): User {
    return {
      id: 'system',
      role: 'system',
      permissions: ['admin'],
    }
  }

  /**
   * Create admin user
   */
  static createAdminUser(id: string): User {
    return {
      id,
      role: 'admin',
      permissions: ['read', 'write', 'execute', 'admin'],
    }
  }

  /**
   * Create regular user
   */
  static createUser(id: string, permissions: Permission[] = ['read']): User {
    return {
      id,
      role: 'user',
      permissions,
    }
  }
}

