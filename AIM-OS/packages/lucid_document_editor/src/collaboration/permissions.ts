/**
 * LUCID Document Editor - Permissions System
 * 
 * Permission management for collaborative editing
 */

export type Permission = 'read' | 'write' | 'comment' | 'admin';

export interface UserPermissions {
  userId: string;
  permissions: Permission[];
}

export interface SectionPermissions {
  sectionId: string;
  defaultPermission: Permission;
  userPermissions: UserPermissions[];
}

export class PermissionManager {
  private documentPermissions: Map<string, Permission[]> = new Map();
  private sectionPermissions: Map<string, SectionPermissions> = new Map();

  /**
   * Set user permissions for document
   */
  setUserPermissions(userId: string, permissions: Permission[]): void {
    this.documentPermissions.set(userId, permissions);
  }

  /**
   * Get user permissions for document
   */
  getUserPermissions(userId: string): Permission[] {
    return this.documentPermissions.get(userId) || ['read'];
  }

  /**
   * Check if user has permission
   */
  hasPermission(userId: string, permission: Permission): boolean {
    const userPermissions = this.getUserPermissions(userId);
    return userPermissions.includes(permission) || userPermissions.includes('admin');
  }

  /**
   * Set section permissions
   */
  setSectionPermissions(sectionId: string, permissions: SectionPermissions): void {
    this.sectionPermissions.set(sectionId, permissions);
  }

  /**
   * Get section permissions
   */
  getSectionPermissions(sectionId: string): SectionPermissions | undefined {
    return this.sectionPermissions.get(sectionId);
  }

  /**
   * Check if user can edit section
   */
  canEditSection(userId: string, sectionId: string): boolean {
    const sectionPerms = this.sectionPermissions.get(sectionId);
    if (sectionPerms) {
      const userPerm = sectionPerms.userPermissions.find(up => up.userId === userId);
      if (userPerm) {
        return userPerm.permissions.includes('write') || userPerm.permissions.includes('admin');
      }
      return sectionPerms.defaultPermission === 'write' || sectionPerms.defaultPermission === 'admin';
    }

    // Fall back to document permissions
    return this.hasPermission(userId, 'write');
  }

  /**
   * Check if user can comment on section
   */
  canCommentOnSection(userId: string, sectionId: string): boolean {
    const sectionPerms = this.sectionPermissions.get(sectionId);
    if (sectionPerms) {
      const userPerm = sectionPerms.userPermissions.find(up => up.userId === userId);
      if (userPerm) {
        return userPerm.permissions.includes('comment') || 
               userPerm.permissions.includes('write') || 
               userPerm.permissions.includes('admin');
      }
      return ['comment', 'write', 'admin'].includes(sectionPerms.defaultPermission);
    }

    // Fall back to document permissions
    return this.hasPermission(userId, 'comment') || this.hasPermission(userId, 'write');
  }

  /**
   * Grant permission to user
   */
  grantPermission(userId: string, permission: Permission): void {
    const current = this.getUserPermissions(userId);
    if (!current.includes(permission)) {
      this.setUserPermissions(userId, [...current, permission]);
    }
  }

  /**
   * Revoke permission from user
   */
  revokePermission(userId: string, permission: Permission): void {
    const current = this.getUserPermissions(userId);
    this.setUserPermissions(userId, current.filter(p => p !== permission));
  }
}

